from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from evaluation.evaluation_scripts import calculate_memory_configs


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


def plot_timing_bit_flips(data_to_check, export_file_name, log=False, minimum=0, maximum=100):
    """
    Plots median bit-flip counts for selected timing parameters across multiple
    memory devices. Filters timing fields, builds grouped centered bar charts,
    applies optional log scaling, and saves the plot as a PDF.

    Args:
        data_to_check (dict): Timing data including memory labels and median values.
        export_file_name (str): Output filename (without extension) for the PDF.
        log (bool): Enables symlog scaling on the y-axis.
        minimum (int): Unused; reserved for future filtering options.
        maximum (int): Y-axis maximum; -1 enables default upper bound.
    """

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
                val = 0  # set invalid measurements to 0
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
        ('MrE35.1', 'yellow', 'Everspin MR4A08BCMA35'),
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


def plot_timing_bit_flips_voltage(data_to_check, export_file_name, log=False, minimum=0, maximum=100,
                                  voltage_range=[3, 0]):
    """
    Plots median bit-flip counts for timing parameters across multiple memory
    devices under different supply voltages. Builds centered grouped bar charts,
    annotates values, applies optional log scaling, and saves the figure as a PDF.

    Args:
        data_to_check (dict): Input data including memory labels and median values.
        export_file_name (str): Name of the output PDF file (without extension).
        log (bool): Enables symlog y-axis scaling.
        minimum (int): Lower y-axis limit.
        maximum (int): Upper y-axis limit; -1 selects default.
        voltage_range (list): X-axis range used for voltage sweeps.
    """
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
                val = 0
            bar_list.append(val)
        bar_dict[mem_label] = bar_list

    x = np.arange(len(list_timing_params))  # x positions
    width = 0.1
    spacing = 0.01

    fig, ax = plt.subplots(layout='constrained', figsize=[15, 5])

    # Device list with label, color, and optional legend name
    device_groups = [
        ('FeLa1', 'green', 'Rohm MR48V256C'),
        ('FeLa2', 'green', None),
        ('FeLa3', 'green', 'Rohm MR48V256C'),
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
        ('Mem 4', 'red', 'Cypress FM22L16 55 TG'),
        ('MrE35.1', 'yellow', 'Everspin MR4A08BCMA35'),
        ('MrE35.2', 'yellow', None),
        ('MrE35.3', 'yellow', 'Everspin MR4A08BCMA35'),
        ('MrE45.R2', 'pink', 'Everspin MR4A08BUYS45'),
        ('MrE45.1', 'pink', 'Everspin MR4A08BUYS45'),
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
                ax.text(pos, val + (maximum * 0.01), f'{val:.0f}', ha='center', va='bottom', fontsize=8, rotation=90)
                bar_positions[i] += 1

    # Label formatting
    ax.set_ylabel('Number of bit-flips')
    ax.set_xticks(x)
    ax.set_xticklabels(list_timing_params)
    ax.set_xlim(voltage_range[0], voltage_range[1])
    if maximum == -1:
        ax.set_ylim(0, 200)
    else:
        ax.set_ylim(minimum, maximum)
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
