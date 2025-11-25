import csv
import logging
from typing import List

import pandas as pd


# ─────────────────────────────────────────────────────────────
# 1. Generic Utility Functions
# ─────────────────────────────────────────────────────────────

def read_csv(file_path: str, delimiter: str = ';', quote_char: str = '\n') -> List[List[int]]:
    """
    Reads a CSV file and prints its contents.

    :param file_path: Path to the CSV file.
    :param delimiter: Character used to separate fields in the CSV file. Default is ';'.
    :param quote_char: Character used to quote fields. Default is newline ('\n').
    """
    try:
        out_values = []
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quote_char)
            for row in reader:
                out_values.append([int(x) for x in row])
        return out_values
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")


def get_timing_zcu102(timing_param: int) -> str:
    """ Maps ZCU102 clock cycles to STM32 timing values (in ns). """
    timing_map = {
        0: '7.57', 1: '9.00', 2: '10.49', 3: '13.00', 4: '15.04', 5: '16.31',
        6: '19.02', 7: '21.20', 8: '23.49', 9: '26.89', 10: '29.14', 11: '31.76',
        12: '35.55', 13: '38.08', 14: '40.61', 15: '42.35', 16: '44.99', 17: '47.12',
        18: '49.18', 19: '52.00', 20: '54.40', 21: '56.55', 22: '59.00', 23: '62.10',
        24: '64.29', 25: '66.59', 26: '70.01', 27: '72.96', 28: '74.97', 29: '77.00',
        30: '79.76', 31: '81.78', 32: '84.01', 33: '87.16', 34: '89.44', 35: '91.69',
        36: '94.83', 37: '96.94', 38: '99.03', 39: '102.11', 40: '104.99', 41: '107.18',
        42: '109.31', 43: '112.43', 44: '114.61', 45: '116.79', 46: '119.93', 47: '122.07',
        48: '124.23', 49: '124.10'
    }

    return timing_map.get(timing_param, 'Unknown')


def get_zcu102_timing_param_map():
    """
    Generate a mapping of adjusted STM32 timing parameter values to their corresponding
    timing configuration strings.

    The mapping is created by adding a set of negative timing offsets to a base value (48),
    then passing each result to the get_timing_stm32() function.

    Returns:
        dict: A dictionary where keys are the adjusted timing parameter integers
              and values are the corresponding configuration strings.
    """
    zcu102_timing_offsets = [-x for x in range(15)]
    return {30 + offset: get_timing_zcu102(30 + offset) for offset in zcu102_timing_offsets}


def get_timing_stm32(timing_param: int) -> str:
    """ Maps ZCU102 clock cycles to STM32 timing values (in ns). """
    timing_map = {
        4: '11.07', 7: '18.54', 10: '27.0', 14: '34.89', 17: '43.42',
        20: '51.86', 24: '62.11', 28: '68.73', 30: '76.95', 34: '85.16',
        36: '96.54', 40: '103.86', 44: '110.52', 48: '119.32'  # TODO: last not verified
    }
    return timing_map.get(timing_param, 'Unknown')


def get_stm32_timing_param_map():
    """
    Generate a mapping of adjusted STM32 timing parameter values to their corresponding
    timing configuration strings.

    The mapping is created by adding a set of negative timing offsets to a base value (48),
    then passing each result to the get_timing_stm32() function.

    Returns:
        dict: A dictionary where keys are the adjusted timing parameter integers
              and values are the corresponding configuration strings.
    """
    stm32_timing_offsets = [0, -4, -8, -12, -14, -18, -20, -24, -28, -31, -34, -38, -41, -44]
    return {48 + offset: get_timing_stm32(48 + offset) for offset in stm32_timing_offsets}


# ─────────────────────────────────────────────────────────────
# 2. Bit Manipulation / Bit-Flip Analysis
# ─────────────────────────────────────────────────────────────


def cmp_binary(x1: int, x2: int, data_width: int = 8) -> int:
    """
    Compares two binary values and returns the number of differing bits
    within the specified bit width.

    Args:
        x1 (int): First binary value.
        x2 (int): Second binary value.
        data_width (int): The bit width for comparison (default is 8).

    Returns:
        int: The number of differing bits between x1 and x2, limited to the given bit width.
    """
    mask = (1 << data_width) - 1
    differing_bits = (x1 ^ x2) & mask

    return bin(differing_bits).count('1')


def calculate_bin_difference(value1: int, value2: int, data_width: int) -> int:
    """
    Calculate the number of differing bits between two integers.

    Args:
    - value1 (int): The first integer value.
    - value2 (int): The second integer value.
    - data_width (int): The width (in bits) of the data to compare.

    Returns:
    - int: The number of differing bits between the two values.
    """
    xor_value = value1 ^ value2
    ctr = 0
    for x in range(0, data_width):
        ctr += 1 if ((xor_value & pow(2, x)) > 0) else 0

    return ctr


def calculate_bit_flips(in_array: List[List[int]], expected_value: int, data_width: int) -> int:
    """
    Calculate the total number of bit flips between each value in an array and an expected value.

    Args:
    - in_array (list): A list of lists, where each inner list contains data to compare.
                        The second element of each inner list is compared to the expected value.
    - expected_value (int): The value to compare each element of in_array against.
    - data_width (int): The width (in bits) of the data to compare.

    Returns:
    - int: The total number of bit flips across all entries in the array.
    """
    total_bit_flips = 0

    for x in in_array:
        if len(x) < 2:
            logging.error(f"Error tuple is to small {len(x)}")
        else:
            total_bit_flips += calculate_bin_difference(x[1], expected_value, data_width)

    return total_bit_flips


def create_panda_table(table_data_dict):
    """
    Converts the provided dictionary of table data into a Pandas DataFrame, configures display options,
    and returns the DataFrame.

    Args:
        table_data_dict (dict): A dictionary where each key represents a column and the values are
                                 the data for that column. The dictionary will be converted into a DataFrame.

    Returns:
        pd.DataFrame: A Pandas DataFrame constructed from the provided dictionary.
    """
    df_write_latency = pd.DataFrame(table_data_dict)

    pd.set_option('display.max_rows', 80)  # Adjust the number of rows to show
    pd.set_option('display.max_columns', None)  # Display all columns

    return df_write_latency
