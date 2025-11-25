import pandas as pd
from matplotlib import pyplot as plt


def plot_platform_timing(config_file: str, board_name: str, board_frequency: int):
    """
    Plot timing characteristics for control signals (CE, WE, OE) based on input CSV data.

    Args:
        config_file (str): Path to the CSV file containing timing data.
        board_name (str): Name of the target board (used for saving the output).
        board_frequency (int): Clock frequency of the board in MHz.
    """

    data = pd.read_csv(config_file)

    cycles = data['cycles'].values
    ce_mean = data['ce_mean'].values
    ce_std = data['ce_std'].values
    we_mean = data['we_mean'].values
    we_std = data['we_std'].values
    oe_mean = data['oe_mean'].values
    oe_std = data['oe_std'].values

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(cycles, ce_mean, yerr=ce_std, fmt='o', capsize=5, markersize=3, label="CE (Average ± Std Dev)")
    ax.errorbar(cycles, we_mean, yerr=we_std, fmt='o', capsize=5, markersize=3, label="WE (Average ± Std Dev)")
    ax.errorbar(cycles, oe_mean, yerr=oe_std, fmt='o', capsize=5, markersize=3, label="OE (Average ± Std Dev)")

    step_size_ns = (1 / board_frequency) * 1000  # Convert clock period to nanoseconds
    step_line = [x * step_size_ns for x in reversed(range(1, len(cycles) + 1))]
    ax.plot(cycles, step_line, linestyle='dashed', color='grey', label=f"Step Size @ {board_frequency} MHz")

    ax.set_xlabel('Data Setup Time in Clock Cycles', fontsize=12)
    ax.set_ylabel('Timing [ns]', fontsize=12)
    ax.set_title('Timing Characteristics for CE, WE, and OE (Mean ± Std Dev)', fontsize=14)

    # Configure y-ticks based on board step size
    ax.set_yticks([(x + 1) * round(step_size_ns, 2) for x in range(len(cycles) + 1)])

    ax.grid(True)
    ax.legend()
