# Memory PUF Evaluation Setup

This repository contains all components required for an extensive evaluation of memory-based PUFs, with a focus on emerging memory technologies such as FRAM, MRAM, and ReRAM. The setup is built around a Xilinx ZCU102 FPGA and is designed to interface with any memory device featuring an SRAM-compatible parallel interface.

The various components included in this repository are illustrated in the following figure:

<div style="text-align: center;"> <img src="doc/figures/overview_setup.svg" style="width: 100%;" alt="FPGA Block Design"> </div>

The components are divided into **hardware** and **software** categories, following the structure of this repository.  

### Hardware

The **hardware** folder contains:  

- **FMC Adapter PCB Layout:**  
  A PCB adapter designed to interface various memory modules with the ZCU102 through its FMC connector. It supports memories with up to 24 address lines and 16 data lines and bridges the logic voltage level differences between the ZCU102 and the connected memory modules. Additionally, it provides options for connecting external power supplies and includes debugging interfaces. The design prioritizes signal integrity and minimizes glitches and noise.

- **FPGA Design:**  
  Contains the FPGA design implementing a custom SRAM memory controller with all timing parameters adjustable at runtime. It supports several types of experiments, including row hammering as well as read and write latency variations. Timing parameters can be tuned with a granularity of 2.5 nanoseconds. The design also includes an AXI interface for communication with the ZCU102’s processing system.
