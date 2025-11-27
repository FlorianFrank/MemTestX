import json
import logging
import statistics
from typing import Optional, List

import numpy as np
import test_defines
from tqdm import tqdm

from evaluation.db_utils import query_database, fetch_memory_instance_details, \
    fetch_memory_type_details, get_reliability_test_configs
from evaluation.defines import DATABASE_PATH, OUTPUT_RESULT_FOLDER, READ_VALUE_IDX, BIT_WDITH
from evaluation.evaluation_utils import _query_and_sort_memory_test_row_hammering, _query_and_sort_memory_test
from evaluation.utils import read_csv, calculate_bit_flips, cmp_binary, get_zcu102_timing_param_map


def check_reliability(array, expected_value, max_address, memory_name, config_file):
    """
    Checks the reliability of data in an array based on expected conditions.

    :param array: List of tuples containing (counter, offset, value, sum_value)
    :param expected_value: Expected value for validation.
    :param max_address: Maximum expected count.
    """
    previous_addr = -1
    list_ok = 0
    err_pos = []

    for i in array:
        address = int(i[0])
        value = int(i[1])
        check_value = int(i[2])

        if address == previous_addr + 1 and value == expected_value and check_value == address + value:
            list_ok += 1
        else:
            err_pos.append(i)

        previous_addr = address
    return list_ok, max_address


def evaluate_test_range(test_type, reduction_param, puf_value, param_mapping_list, metric='median'):
    """Evaluate test behavior over a set of parameters for a given PUF configuration.

    Args:
        test_type (TestType): Type of the test (e.g., WRITE_LATENCY, READ_LATENCY).
        reduction_param (str): Parameter name used for timing reduction.
        puf_value (int): PUF value used for evaluation.
        param_mapping_list (dict): Mapping of parameter keys to readable labels.
        metric (str): Metric to evaluate ('median' or 'mean').

    Returns:
        dict: Structured table containing memory info and statistical results.
    """
    # Initialize table data structure
    table_data = {
        'memoryLabels': [],
        'instanceIDs': []
    }

    # Add result columns for each parameter entry
    for label in param_mapping_list.values():
        table_data[f'{label} ({metric})'] = []

    for label in param_mapping_list.values():
        table_data[f'{label} (std)'] = []

    memory_ids = []
    memory_labels = []

    # Get memory instance configurations
    memory_configs = calculate_memory_configs()
    for cfg in memory_configs:
        if cfg[0] not in memory_ids:
            memory_ids.append(cfg[0])
        if cfg[1] not in memory_labels:
            memory_labels.append(cfg[1])

    print("Evaluating memory instances...")

    for mem_id, label in tqdm(zip(memory_ids, memory_labels), total=len(memory_ids), desc="Progress"):
        if not isinstance(mem_id, int):
            continue

        eval_dict, cfg = calculate_hamming_weights(test_type, mem_id, puf_value, reduction_param)
        if len(eval_dict.keys()) == 0:
            continue

        table_data['memoryLabels'].append(label)
        table_data['instanceIDs'].append(mem_id)

        # print(eval_dict)
        timing_param_default = 0
        if cfg:
            timing_param_default = int(cfg[next(iter(cfg))]['timing'].get(reduction_param, 0))

        for key, label in param_mapping_list.items():
            relative_key = key - timing_param_default
            # UGLY HACK solve it
            if test_type == test_defines.TestType.READ_LATENCY:
                relative_key -= 30
            measurements = eval_dict.get(relative_key)

            if measurements:
                max_addr = cfg.get(relative_key, {}).get('max_addr', 1)
                data_width = cfg.get(relative_key, {}).get('data_width', 1)
                scale_factor = max_addr * data_width

                central_value = statistics.median(measurements) if metric == 'median' else statistics.mean(measurements)
                central_value = (central_value / scale_factor) * 100

                std_dev = (statistics.stdev(measurements) / scale_factor) * 100 if len(measurements) > 1 else 0
            else:
                central_value = -1
                std_dev = -1

            table_data[f'{label} ({metric})'].append(central_value)
            table_data[f'{label} (std)'].append(std_dev)

    return table_data


def calculate_hamming_weights(test: test_defines.TestType, memory_id: int, target_puf_value: int, param_key: str):
    """
    Compute bit-flip counts for entries matching a PUF value. Entries are grouped by
    `param_key`, their CSV data is loaded, and bit flips are calculated per group.

    Returns:
        (result_map, config_map): bit-flip results and related config data.
    """

    grouped_entries = _query_and_sort_memory_test(test, memory_id, target_puf_value, param_key)

    result_map = dict()
    config_map = dict()

    if grouped_entries:
        for index in range(len(next(iter(grouped_entries.values())))):
            for param_value, entries in grouped_entries.items():
                if len(entries) > index:
                    csv_data = read_csv(f'{OUTPUT_RESULT_FOLDER}/{entries[index]["config_file"]}')

                    config_map[round(float(param_value), 3)] = {
                        'data_width': entries[index]["data_width"],
                        'max_addr': entries[index]["max_addr"],
                        'timing': entries[index]["timing"]
                    }
                    if csv_data:
                        bit_flips = calculate_bit_flips(csv_data, int(entries[index]['puf_value']),
                                                        int(entries[index]["data_width"]))
                        result_map.setdefault(round(float(param_value), 3), []).append(bit_flips)
                    else:
                        print("Error no csv data!")
    return result_map, config_map


def evaluate_intra_hamming_distance(test: test_defines.TestType, memory_id: int, puf_value: int, selected_param: str,
                                    timing_value: int = 0) -> List[float]:
    """
    Evaluate the intra Hamming distance based on the given parameters.

    Args:
    - test (test_defines.TestType): The type of test being performed.
    - memory_id (int): The ID of the memory.
    - puf_value (int): The PUF value to filter entries.
    - selected_param (str): The parameter by which to sort and group entries.
    - timing_value (int, optional): The timing value to filter entries. Default is 0.

    Returns:
    - List[float]: The list of Hamming distances as percentages.
    """

    grouped_by_param = _query_and_sort_memory_test(test, memory_id, puf_value, selected_param)

    csv_files: List[List[int]] = []
    max_addr = 0

    # Read CSV files all belonging to one memory instance measured under same conditions
    for key, entries in grouped_by_param.items():
        for entry in entries:
            if entry[selected_param] == timing_value:
                bit_width = int(entry["data_width"])
                max_addr = entry["max_addr"]
                csv_data = read_csv(f'{OUTPUT_RESULT_FOLDER}/{entry["config_file"]}')
                csv_files.append([int(x[READ_VALUE_IDX]) for x in csv_data])

    # Calculate hamming distance among those
    bit_differences_list = []
    for i, csv_file1 in enumerate(csv_files):
        for j, csv_file2 in enumerate(csv_files):
            bit_ctr = 0
            for x, y in zip(csv_file1, csv_file2):
                bit_ctr += cmp_binary(x, y, data_width=BIT_WDITH)
            hamming_distance = (bit_ctr / (max_addr * BIT_WDITH)) * 100
            bit_differences_list.append(hamming_distance)

    return bit_differences_list


def evaluate_inter_hamming_distance(test: test_defines.TestType, memory_id1: int, memory_id2: int, puf_value: int,
                                    selected_param: str,
                                    timing_value: int = 0) -> Optional[List[float]]:
    """
    Compute inter-device Hamming distances by comparing CSV data from two memory IDs
    filtered by PUF value and a selected parameter.

    Returns:
        List of Hamming distance percentages, or None on incompatible configs.
    """

    grouped_by_param1 = _query_and_sort_memory_test(test, memory_id1, puf_value, selected_param)
    grouped_by_param2 = _query_and_sort_memory_test(test, memory_id2, puf_value, selected_param)

    csv_files1: List[List[int]] = []
    csv_files2: List[List[int]] = []
    max_addr = 0

    for key in grouped_by_param1.keys():
        for entry1, entry2 in zip(grouped_by_param1[key], grouped_by_param2[key]):
            if entry1[selected_param] == timing_value and entry2[selected_param] == timing_value:
                bit_width1 = int(entry1["data_width"])
                bit_width2 = int(entry2["data_width"])
                if bit_width1 != bit_width2:
                    logging.error("Bit width does not match! Selected two different memory types.")
                    return None

                max_addr1 = int(entry1["max_addr"])
                max_addr2 = int(entry2["max_addr"])
                if max_addr1 != max_addr2:
                    logging.error("Two maximum addresses!")
                    return None
                max_addr = max_addr1

                csv_data1 = read_csv(f'{OUTPUT_RESULT_FOLDER}/{entry1["config_file"]}')
                csv_data2 = read_csv(f'{OUTPUT_RESULT_FOLDER}/{entry1["config_file"]}')
                csv_files1.append([int(x[READ_VALUE_IDX]) for x in csv_data1])
                csv_files2.append(([int(x[READ_VALUE_IDX]) for x in csv_data2]))

    bit_differences_list = []
    for i, csv_file1 in enumerate(csv_files1):
        for j, csv_file2 in enumerate(csv_files2):
            bit_ctr = 0
            if csv_file1[0] != -1 and csv_file2[0] != -1:
                for x, y in zip(csv_file1, csv_file2):
                    bit_ctr += cmp_binary(x, y, data_width=BIT_WDITH)
                hamming_distance = (bit_ctr / (max_addr * BIT_WDITH)) * 100
                bit_differences_list.append(hamming_distance)

    return bit_differences_list


def calculate_box_plot_data(data_list, irq_factor: int = 1.5, lower_percentile: int = 25, upper_percentile: int = 75,
                            resolution: int = 2):
    """
    Calculate the statistics for box plots from a list of data. This includes the minimum,
    first quartile (Q1), median, third quartile (Q3), maximum, and outliers.

    Args:
    - irq_factor (int): The factor used to calculate the upper and lower bounds for outliers (default is 1.5).

    Returns:
    - None: This function prints out the statistics required for box plots.
    """

    boxplot_stats = []

    for data in data_list:
        min_val = np.min(data)
        q1 = np.percentile(data, lower_percentile)
        median = np.mean(data)
        q3 = np.percentile(data, upper_percentile)
        max_val = np.max(data)

        iqr = q3 - q1
        lower_bound = q1 - irq_factor * iqr
        upper_bound = q3 + irq_factor * iqr
        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        boxplot_stats.append(
            {'min': min_val, 'q1': q1, 'median': median, 'q3': q3, 'max': max_val, 'outliers': outliers})

    # Print out the required values for TikZ plotting
    for i, stats in enumerate(boxplot_stats):
        print(f"median={round(stats['median'], resolution)}")
        print(f"upper quartile={round(stats['q3'], resolution)}")
        print(f"lower quartile={round(stats['q1'], resolution)}")
        print(f"upper whisker={round(stats['max'], resolution)}")
        print(f"lower whisker={round(stats['min'], resolution)}")

        print(f"Dataset {i + 1} (FRAM {i + 1}):")
        print(f"  Outliers: {stats['outliers']}")
        print("")

    print(statistics.mean([x['median'] for x in boxplot_stats]))


def calculate_memory_configs() -> list:
    """
    Processes all reliability test configs by loading memory details, parsing
    test parameters, reading result CSVs, and computing per-memory reliability.
    Returns a list of results sorted by memory label.
    """
    memory_label_id_list = []
    reliable_table = []

    # Fetch test configurations from the database
    test_configs = get_reliability_test_configs(mem_name='all')

    for test_config in test_configs:
        memory_instance_id, config_file, test_parameter_json, test_id = test_config

        memory_instance = fetch_memory_instance_details(memory_instance_id)
        if not memory_instance:
            continue

        memory_label, memory_type_id = memory_instance[0]
        if [memory_instance_id, memory_label] not in memory_label_id_list:
            memory_label_id_list.append([memory_instance_id, memory_label])

        memory_type = fetch_memory_type_details(memory_type_id)
        if memory_type:
            memory_name, data_width, max_address = memory_type[0]
        else:
            continue
        try:
            test_params = json.loads(test_parameter_json)
            init_value = int(test_params.get("init_value", 0)) & ((1 << int(data_width)) - 1)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logging.error(f"Error while parsing test parameters for test ID {test_id}: {e}")
            continue
        try:
            csv_data = read_csv(f'../output_results/{config_file}')
            correct_values, total_addr = check_reliability(csv_data, int(init_value), max_address + 1, memory_label,
                                                           config_file)
            reliable_table.append(
                [memory_instance_id, memory_label, config_file, correct_values, total_addr, init_value])
        except TypeError:
            logging.error(f"File {config_file} not found!")

    return sorted(reliable_table, key=lambda x: x[1])


def calculate_hamming_weights_row_hammering(test: test_defines.TestType, memory_id: int, target_puf_value: int):
    """
    Compute bit-flip (Hamming weight) results for row-hammering tests by:
    1) grouping test entries by hammering parameters,
    2) reading their associated CSV output data,
    3) calculating bit flips per entry, and
    4) returning the results along with configuration metadata.
    """
    grouped_entries = _query_and_sort_memory_test_row_hammering(test, memory_id, target_puf_value)

    result_map = dict()
    config_map = dict()

    if grouped_entries:
        for index in range(len(next(iter(grouped_entries.values())))):
            for param_value, entries in grouped_entries.items():
                if len(entries) > index:
                    csv_data = read_csv(f'{OUTPUT_RESULT_FOLDER}/{entries[index]["config_file"]}')

                    config_map[param_value] = {
                        'data_width': entries[index]["data_width"],
                        'max_addr': entries[index]["max_addr"],
                        'timing': entries[index]["timing"]
                    }
                    if csv_data:
                        bit_flips = calculate_bit_flips(csv_data, int(entries[index]['puf_value']),
                                                        int(entries[index]["data_width"]))
                        result_map.setdefault(param_value, []).append(bit_flips)
                    else:
                        print("Error no csv data!")
    return result_map, config_map


def evaluate_row_hammering_range(puf_value, metric='median'):
    """
       Evaluate test behavior over a set of parameters for a given row hammering PUF configuration.

       Args:
           test_type (TestType): Type of the test (e.g., WRITE_LATENCY, READ_LATENCY).
           reduction_param (str): Parameter name used for timing reduction.
           puf_value (int): PUF value used for evaluation.
           param_mapping_list (dict): Mapping of parameter keys to readable labels.
           metric (str): Metric to evaluate ('median' or 'mean').

       Returns:
           dict: Structured table containing memory info and statistical results.
       """
    # Initialize table data structure
    table_data = {
        'memoryLabels': [],
        'instanceIDs': []
    }

    memory_ids = []
    memory_labels = []

    param_mapping_list = {(64, 100): "64/100", (64, 1000): "64/1000", (64, 10000): "64/10000",
                          (64, 100000): "64/100000",
                          (128, 100): "128/100", (128, 1000): "128/1000", (128, 10000): "128/10000",
                          (128, 100000): "128/100000",
                          (256, 100): "256/100", (256, 1000): "256/1000", (256, 10000): "256/10000",
                          (256, 100000): "256/100000",
                          (512, 100): "512/100", (512, 1000): "512/1000", (512, 10000): "512/10000",
                          (512, 100000): "512/100000",
                          (1024, 100): "1024/100", (1024, 1000): "1024/1000", (1024, 10000): "1024/10000",
                          (1024, 100000): "1024/100000"}

    for label in param_mapping_list.values():
        table_data[f'{label} ({metric})'] = []

    for label in param_mapping_list.values():
        table_data[f'{label} (std)'] = []

    # Get memory instance configurations
    memory_configs = calculate_memory_configs()
    for cfg in memory_configs:
        if cfg[0] not in memory_ids:
            memory_ids.append(cfg[0])
        if cfg[1] not in memory_labels:
            memory_labels.append(cfg[1])

    for mem_id, label in tqdm(zip(memory_ids, memory_labels), total=len(memory_ids), desc="Progress"):
        if not isinstance(mem_id, int):
            continue
        eval_dict, cfg = calculate_hamming_weights_row_hammering(test_defines.TestType.ROW_HAMMERING, mem_id, puf_value)
        if len(eval_dict.keys()) == 0:
            continue

        table_data['memoryLabels'].append(label)
        table_data['instanceIDs'].append(mem_id)

        for key, label in param_mapping_list.items():
            relative_key = key
            measurements = eval_dict.get(relative_key)

            if measurements:
                max_addr = cfg.get(relative_key, {}).get('max_addr', 1)
                data_width = cfg.get(relative_key, {}).get('data_width', 1)
                scale_factor = max_addr * data_width

                central_value = statistics.median(measurements) if metric == 'median' else statistics.mean(measurements)
                central_value = (central_value / scale_factor) * 100

                std_dev = (statistics.stdev(measurements) / scale_factor) * 100 if len(measurements) > 1 else 0
            else:
                central_value = -1
                std_dev = -1

            table_data[f'{label} ({metric})'].append(central_value)
            table_data[f'{label} (std)'].append(std_dev)

    return table_data


def evaluate_test_range_row_hammering(test_type, reduction_param, puf_value, param_mapping_list, metric='median'):
    """
    Evaluate test behavior over a set of parameters for a given PUF configuration.

    Args:
        test_type (TestType): Type of the test (e.g., WRITE_LATENCY, READ_LATENCY).
        reduction_param (str): Parameter name used for timing reduction.
        puf_value (int): PUF value used for evaluation.
        param_mapping_list (dict): Mapping of parameter keys to readable labels.
        metric (str): Metric to evaluate ('median' or 'mean').

    Returns:
        dict: Structured table containing memory info and statistical results.
    """
    # Initialize table data structure
    table_data = {
        'memoryLabels': [],
        'instanceIDs': []
    }

    # Add result columns for each parameter entry
    for label in param_mapping_list.values():
        table_data[f'{label} ({metric})'] = []

    for label in param_mapping_list.values():
        table_data[f'{label} (std)'] = []

    memory_ids = []
    memory_labels = []

    # Get memory instance configurations
    memory_configs = calculate_memory_configs()
    for cfg in memory_configs:
        if cfg[0] not in memory_ids:
            memory_ids.append(cfg[0])
        if cfg[1] not in memory_labels:
            memory_labels.append(cfg[1])

    print("Evaluating memory instances...")

    for mem_id, label in tqdm(zip(memory_ids, memory_labels), total=len(memory_ids), desc="Progress"):
        if not isinstance(mem_id, int):
            continue

        eval_dict, cfg = calculate_hamming_weights(test_type, mem_id, puf_value, reduction_param)
        if len(eval_dict.keys()) == 0:
            continue

        table_data['memoryLabels'].append(label)
        table_data['instanceIDs'].append(mem_id)

        # print(eval_dict)
        timing_param_default = 0
        if cfg:
            timing_param_default = int(cfg[next(iter(cfg))]['timing'].get(reduction_param, 0))

        for key, label in param_mapping_list.items():
            relative_key = key - timing_param_default
            # UGLY HACK solve it
            if test_type == test_defines.TestType.READ_LATENCY:
                relative_key -= 30
            measurements = eval_dict.get(relative_key)

            if measurements:
                max_addr = cfg.get(relative_key, {}).get('max_addr', 1)
                data_width = cfg.get(relative_key, {}).get('data_width', 1)
                scale_factor = max_addr * data_width

                central_value = statistics.median(measurements) if metric == 'median' else statistics.mean(measurements)
                central_value = (central_value / scale_factor) * 100

                std_dev = (statistics.stdev(measurements) / scale_factor) * 100 if len(measurements) > 1 else 0
            else:
                central_value = -1
                std_dev = -1

            table_data[f'{label} ({metric})'].append(central_value)
            table_data[f'{label} (std)'].append(std_dev)

    return table_data


def evaluate_voltage_test(test_type, reduction_param, puf_value, metric):
    """
    Evaluate voltage-related tests by generating a parameter map of voltage values.
    """
    param_mapping_list = {
        round(-(0.001 * i), 3): f'{round(0.02 - (0.001 * i), 3)}' for i in range(20)
    }
    return evaluate_test_range(test_type, reduction_param, puf_value, param_mapping_list, metric)


def evaluate_row_hammering_test(puf_value, metric):
    return evaluate_row_hammering_range(puf_value, metric)


def evaluate_latency_test(test_type, reduction_param, puf_value, metric, board):
    """
    Evaluate latency-related tests using STM32 timing parameters.
    """
    return evaluate_test_range(test_type, reduction_param, puf_value, get_zcu102_timing_param_map(), metric)