from collections import defaultdict
from typing import Optional

from evaluation.defines import HAMMING_DISTANCE_IDENTIFIER, PUF_VALUE_IDENTIFIER, \
    HAMMING_ITERATIONS_IDENTIFIER
from src.test_scheduling import test_defines


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

        # Retrieve and parse all timing values
        query = f"""
            SELECT * FROM memory_timing_config WHERE name = ? 
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


def _query_and_sort_memory_test_row_hammering(test: test_defines.TestType, memory_id: int, target_puf_value: int):
    """
    Filter memory test config by PUF value, sort by hammering distance/iterations (desc),
    and group entries by those hammering parameters.
    """
    latency_config = query_memory_test_config(test, memory_instance=None, memory_id=memory_id)
    filtered_entries = [entry for entry in latency_config if entry[PUF_VALUE_IDENTIFIER] == target_puf_value]

    sorted_entries = sorted(filtered_entries,
                            key=lambda x: (-x[HAMMING_DISTANCE_IDENTIFIER], -x[HAMMING_ITERATIONS_IDENTIFIER]),
                            reverse=True)

    grouped_entries = defaultdict(list)
    for entry in sorted_entries:
        group_key = (entry[HAMMING_DISTANCE_IDENTIFIER], entry[HAMMING_ITERATIONS_IDENTIFIER])
        grouped_entries[group_key].append(entry)

    return grouped_entries


def _query_and_sort_memory_test(test: test_defines.TestType, memory_id: int, target_puf_value: int, param_key: str):
    """
    Filter memory test config by PUF value, sort by the given parameter (desc),
    and group entries by that parameter value.
    """
    latency_config = query_memory_test_config(test, memory_instance=None, memory_id=memory_id)

    filtered_entries = [entry for entry in latency_config if entry['puf_value'] == target_puf_value]

    sorted_entries = sorted(filtered_entries, key=lambda x: x[param_key], reverse=True)

    grouped_entries = defaultdict(list)
    for entry in sorted_entries:
        grouped_entries[entry[param_key]].append(entry)
    return grouped_entries
