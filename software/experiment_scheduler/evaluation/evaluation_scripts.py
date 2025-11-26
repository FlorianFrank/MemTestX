import json
import logging
import statistics
from collections import defaultdict
from typing import Optional, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm

import test_defines
from evaluation.db_utils import query_database, fetch_memory_instance_details, \
    fetch_memory_type_details, get_reliability_test_configs
from evaluation.defines import DATABASE_PATH
from evaluation.utils import read_csv, calculate_bit_flips, cmp_binary, get_stm32_timing_param_map, \
    get_zcu102_timing_param_map


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


def _query_and_sort_memory_test_row_hammering(test: test_defines.TestType, memory_id: int, target_puf_value: int):
    latency_config = query_memory_test_config(test, memory_instance=None, memory_id=memory_id)
    filtered_entries = [entry for entry in latency_config if entry['puf_value'] == target_puf_value]

    sorted_entries = sorted(filtered_entries, key=lambda x: (-x['hammeringDistance'], -x['hammeringIterations']),
                            reverse=True)

    grouped_entries = defaultdict(list)
    for entry in sorted_entries:
        group_key = (entry['hammeringDistance'], entry['hammeringIterations'])
        grouped_entries[group_key].append(entry)

    return grouped_entries


def _query_and_sort_memory_test(test: test_defines.TestType, memory_id: int, target_puf_value: int, param_key: str):
    latency_config = query_memory_test_config(test, memory_instance=None, memory_id=memory_id)

    filtered_entries = [entry for entry in latency_config if entry['puf_value'] == target_puf_value]

    sorted_entries = sorted(filtered_entries, key=lambda x: x[param_key], reverse=True)

    grouped_entries = defaultdict(list)
    for entry in sorted_entries:
        grouped_entries[entry[param_key]].append(entry)
    return grouped_entries


def calculate_hamming_weights_row_hammering(test: test_defines.TestType, memory_id: int, target_puf_value: int):
    grouped_entries = _query_and_sort_memory_test_row_hammering(test, memory_id, target_puf_value)

    result_map = dict()
    config_map = dict()

    if grouped_entries:
        for index in range(len(next(iter(grouped_entries.values())))):
            for param_value, entries in grouped_entries.items():
                if len(entries) > index:
                    csv_data = read_csv(f'../output_results/{entries[index]["config_file"]}')

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


def calculate_hamming_weights(test: test_defines.TestType, memory_id: int, target_puf_value: int, param_key: str):
    """
    Calculates the Hamming weights (bit flips) for entries matching a specified PUF value.
    The entries are filtered, sorted, and grouped by a selected parameter. For each group,
    the corresponding configuration data is read from CSV files, and bit flips are calculated
    based on the configuration.

    Args:
        test: The test configuration containing memory parameters.
        memory_id: The ID of the memory instance to query.
        target_puf_value: The PUF value to filter the entries by.
        param_key: The key used to group and sort the entries (e.g., 'tPWDWrite').

    Returns:
        A tuple containing:
            - A dictionary (`result_map`) mapping rounded parameter values to lists of calculated bit flips.
            - A dictionary (`config_map`) mapping rounded parameter values to configuration details.
    """

    grouped_entries = _query_and_sort_memory_test(test, memory_id, target_puf_value, param_key)

    result_map = dict()
    config_map = dict()

    if grouped_entries:
        for index in range(len(next(iter(grouped_entries.values())))):
            for param_value, entries in grouped_entries.items():
                if len(entries) > index:
                    csv_data = read_csv(f'../output_results/{entries[index]["config_file"]}')

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
    bit_width = 8
    max_addr = 0

    for key, entries in grouped_by_param.items():
        for entry in entries:
            if entry[selected_param] == timing_value:
                bit_width = int(entry["data_width"])
                max_addr = entry["max_addr"]
                csv_data = read_csv(f'../output_results/{entry["config_file"]}')
                csv_files.append([int(x[1]) for x in csv_data])

    bit_differences_list = []
    for i, csv_file1 in enumerate(csv_files):
        for j, csv_file2 in enumerate(csv_files):
            if i != j and not (memory_id == 15 and (i == 4 or j == 4)):
                bit_ctr = 0
                for x, y in zip(csv_file1, csv_file2):
                    bit_ctr += cmp_binary(x, y, data_width=bit_width)
                hamming_distance = (bit_ctr / (max_addr * bit_width)) * 100
                bit_differences_list.append(hamming_distance)

    return bit_differences_list


def evaluate_inter_hamming_distance(test: test_defines.TestType, memory_id1: int, memory_id2: int, puf_value: int,
                                    selected_param: str,
                                    timing_value: int = 0) -> Optional[List[float]]:
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

    grouped_by_param1 = _query_and_sort_memory_test(test, memory_id1, puf_value, selected_param)
    grouped_by_param2 = _query_and_sort_memory_test(test, memory_id2, puf_value, selected_param)

    csv_files1: List[List[int]] = []
    csv_files2: List[List[int]] = []
    bit_width = 8
    max_addr = 0

    for key in grouped_by_param1.keys():
        for entry1, entry2 in zip(grouped_by_param1[key], grouped_by_param2[key]):
            if entry1[selected_param] == timing_value and entry2[selected_param] == timing_value:
                bit_width1 = int(entry1["data_width"])
                bit_width2 = int(entry2["data_width"])
                if bit_width1 != bit_width2:
                    logging.error("Bit width does not match! Selected two different memory types.")
                    return None
                bit_width = bit_width1

                max_addr1 = int(entry1["max_addr"])
                max_addr2 = int(entry2["max_addr"])
                if max_addr1 != max_addr2:
                    logging.error("Two maximum addresses!")
                    return None
                max_addr = max_addr1

                csv_data1 = read_csv(f'../output_results/{entry1["config_file"]}')
                csv_data2 = read_csv(f'../output_results/{entry1["config_file"]}')
                csv_files1.append([int(x[1]) for x in csv_data1])
                csv_files2.append(([int(x[1]) for x in csv_data2]))

    bit_differences_list = []
    for i, csv_file1 in enumerate(csv_files1):
        for j, csv_file2 in enumerate(csv_files2):
            if not ((memory_id1 == 15 or memory_id2 == 15) and (i == 4 or j == 4)):
                bit_ctr = 0
                if csv_file1[0] != -1 and csv_file2[0] != -1:
                    for x, y in zip(csv_file1, csv_file2):
                        bit_ctr += cmp_binary(x, y, data_width=bit_width)
                    hamming_distance = (bit_ctr / (max_addr * bit_width)) * 100
                    bit_differences_list.append(hamming_distance)

    return bit_differences_list


def query_memory_test_config(test_type: test_defines.TestType, memory_instance: Optional[str],
                             memory_id: Optional[int]):
    """
    Queries the memory test configuration based on test type and memory instance.

    :param test_type: The type of test to query.
    :param memory_instance: The memory instance name (if specified).
    :param memory_id: The memory ID (if specified).
    """
    test_type_str = test_defines.test_type_to_str(test_type)

    where_clause = ""  # SELECT ALL BY DEFAULT
    where_params = [test_type_str]  # Initialize with the test_type parameter.

    if memory_id is not None and memory_instance is None:
        where_clause = "AND tc.memory_instance_id = ?"
        where_params.append(memory_id)
    elif memory_instance and memory_id is None:  # Ensures memory_instance is not empty
        where_clause = "AND mi.label = ?"
        where_params.append(memory_instance)

    # Build the query
    query = f"""
        SELECT mi.label, m.name, m.data_width, tc.config_file, tc.test_parameter_json, m.max_addr 
        FROM memory_instances AS mi
        JOIN test_configs AS tc ON mi.id = tc.memory_instance_id
        JOIN memories AS m ON mi.memory_type_id = m.id
        WHERE tc.test_type = ? 
        {where_clause}
    """

    # Execute the query with the appropriate parameters

    return_value = query_database(DATABASE_PATH, query, tuple(where_params))

    list_ret_dict = []
    for timing_entry in return_value:
        ret_json = json.loads(timing_entry[4])
        ret_json['label'] = timing_entry[0]
        ret_json['type'] = timing_entry[1]
        ret_json['data_width'] = int(timing_entry[2])
        ret_json['config_file'] = timing_entry[3]
        ret_json['max_addr'] = timing_entry[5]

        # TODO was soll das?
        query = f"""
            SELECT * 
            FROM memory_timing_config 
            WHERE name = ? 
        """
        return_timing = query_database(DATABASE_PATH, query, tuple([timing_entry[1]]))
        for timing_entry in return_timing:
            ret_json['timing'] = {'ceDrivenWrite': timing_entry[3], 'ceDrivenRead': timing_entry[4],
                                  'tWaitAfterInit': timing_entry[5],
                                  'tNextRead': timing_entry[6], 'tStartWrite': timing_entry[7],
                                  'tNextWrite': timing_entry[8], 'tACWrite': timing_entry[9],
                                  'tASWrite': timing_entry[10], 'tAHWrite': timing_entry[11],
                                  'tPWDWrite': timing_entry[12], 'tDSWrite': timing_entry[13],
                                  'tDHWrite': timing_entry[14], 'tStartRead': timing_entry[15],
                                  'tASRead': timing_entry[16], 'tAHRead': timing_entry[17],
                                  'tOEDRead': timing_entry[18],
                                  'tPRCRead': timing_entry[19], 'tCEOEEnableRead': timing_entry[20],
                                  'tCEOEDisableRead': timing_entry[21]}

        list_ret_dict.append(ret_json)

    return list_ret_dict


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
        median = np.mean(data)  # TODO
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


def plot_multiple_box_plots(data: List[List[int]], out_name: str, labels: List[str], x_label, y_label):
    """
    Plots multiple box plots from a list of datasets and saves the plot as a TikZ file for LaTeX.

    Args:
    - data (List[List[int]]): A list of datasets to plot. Each dataset is a list of integers.
    - out_name (str): The name of the output TikZ file (without the .tikz extension).
    - labels (List[str]): A list of labels corresponding to each dataset.
    - x_label (str): The label for the x-axis.
    - y_label (str): The label for the y-axis.

    Returns:
    - None: The function saves the plot as a TikZ file and does not return anything.
    """

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, patch_artist=True, medianprops=dict(color='black'))

    plt.xticks(range(1, len(data) + 1), labels)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()

    # tikzplotlib.save(f"export/tex/{out_name}.tikz")


def plot_reliability_table(ratio_passed: float = 0.9):
    """
    Generates and returns a DataFrame summarizing the reliability of memory configurations.

    The table includes memory IDs, labels, initial values, correct address counts,
    total address counts, reliability ratios, status indicators (✔/✘), and config file names.
    Redundant memory IDs and labels are suppressed for readability.
    """

    memory_configs = calculate_memory_configs()

    seen_ids = set()
    seen_labels = set()

    data = {'MemoryIDs': [], 'MemoryLabels': [], 'InitValue': [], 'Correct': [], 'TotalAddresses': [], 'Ratio': [],
            'Status': [], 'ConfigFiles': []
            }

    for mem_id, label, config_file, correct, total, init_val in memory_configs:
        data['MemoryIDs'].append(mem_id if mem_id not in seen_ids else '')
        data['MemoryLabels'].append(label if label not in seen_labels else '')
        data['ConfigFiles'].append(config_file)
        data['Correct'].append(correct)
        data['TotalAddresses'].append(total)
        data['InitValue'].append(hex(init_val))

        seen_ids.add(mem_id)
        seen_labels.add(label)

        ratio = correct / total if total != 0 else 0.0
        data['Ratio'].append(ratio)
        data['Status'].append('✔' if ratio > ratio_passed else '✘')

    df = pd.DataFrame(data)

    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', None)

    return df


def calculate_memory_configs():
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


def evaluate_row_hammering_range(puf_value, metric='median'):
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

    print(memory_configs)

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


def evaluate_test_range(test_type, reduction_param, puf_value, param_mapping_list, metric='median'):
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

def plot_timing_bit_flips(data_to_check, export_file_name, log=False, minimum=0, maximum=100):
    # Filter relevant timing parameters
    list_timing_params = []
    for x in data_to_check.keys():
        if 'median' in x:
            if float(x.replace(' (median)', '')) < 100:
                list_timing_params.append(x.replace(' (median)', ''))

    # Prepare the bar data
    bar_dict = {}
    for mem_label in data_to_check['memoryLabels']:
        bar_list = []
        for param in list_timing_params:
            val = data_to_check[f'{param} (median)'][data_to_check['memoryLabels'].index(mem_label)]
            if val == -1:
                #if val < 0.5: TODO ADD AGAIN
                val = 0
            bar_list.append(val)
        bar_dict[mem_label] = bar_list

    x = np.arange(len(list_timing_params))  # x positions
    width = 0.04
    spacing = 0.01

    fig, ax = plt.subplots(layout='constrained', figsize=[15, 5])

    # Device list with label, color, and optional legend name
    device_groups = [
        ('FeLa1', 'green', 'Rohm MR48V256C'),
        ('FeLa2', 'green', None),
        ('FeLa3', 'green', None),
        ('FeLa4', 'green', None),
        ('FeLa5', 'green', None),
        ('FeLa6', 'green', None),
        ('FeLa7', 'green', None),
        ('FeLa8', 'green', None),
        ('FeLa9', 'green', None),
        ('FeLa10', 'green', None),
        ('FRAM R5', 'green', None),
        ('FeFJ1', 'blue', 'FRAM Fujitsu MB85R1001ANC'),
        ('FeFJ3', 'blue', None),
        ('FeFJ4', 'blue', None),
        ('FeFJ2', 'blue', None),
        ('FeFJ5', 'blue', None),
        ('FeFJ6', 'blue', None),
        ('Mem 1', 'red', 'Cypress FM22L16 55 TG'),
        ('Mem 4', 'red', None),
        ('Mem 1', 'yellow', 'Everspin MR4A08BCMA35'),
        ('MrE35.1', 'yellow', None),
        ('MrE35.1', 'yellow', None),
        ('MrE35.2', 'yellow', None),
        ('MrE35.3', 'yellow', None),
        ('MrE45.R2', 'pink', 'Everspin MR4A08BUYS45'),
        ('MrE45.1', 'pink', None),
    ]

    # Calculate total non-zero bars per timing_param to compute centering
    non_zero_bars_per_param = [0] * len(list_timing_params)
    for _, _, _ in device_groups:
        for i, val in enumerate(bar_dict.get(_, [0] * len(list_timing_params))):
            if val > 0:
                non_zero_bars_per_param[i] += 1

    # Plot dynamically, centered per label
    offsets_per_param = [[] for _ in range(len(list_timing_params))]
    bar_positions = [0] * len(list_timing_params)  # track used width per x label

    for device, color, label in device_groups:
        values = bar_dict.get(device, [])
        if sum(values) == 0:
            continue  # skip plotting if all bars are zero

        for i, val in enumerate(values):
            if val > 0:
                # Compute offset centered around the timing_param index
                total_width = non_zero_bars_per_param[i] * (width + spacing)
                start = -total_width / 2 + bar_positions[i] * (width + spacing)
                pos = x[i] + start
                ax.bar(pos, val, width, color=color, label=label if label else None)
                bar_positions[i] += 1

    # Label formatting
    ax.set_ylabel('Number of bit-flips')
    ax.set_xlabel('Timing value [ns]')
    ax.set_xticks(x)
    ax.set_xticklabels(list_timing_params)
    if maximum == -1:
        ax.set_ylim(0, 110)
    if log:
        ax.set_yscale('symlog')

    # Deduplicate legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', ncol=1)
    ax.grid(True)
    # plt.show()
    fig.savefig(f"../export/pdf/{export_file_name}.pdf")

    #tikzplotlib.save(f"export/tex/{export_file_name}.tikz")

