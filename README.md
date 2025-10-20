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

### Software

The **software** folder contains:  

- **PS Software:**  
  Implements the firmware running on the Processing System (PS) of the ZCU102. It manages communication with the PL to schedule and control experiments, as well as to receive measurement data through the same interface.  
  Additionally, it provides a network interface for receiving commands and parameters from an external program hosting the experiment scheduler (described below). The firmware also transmits the collected measurement data back to this external program for persistent storage and further analysis.

- **Test Scheduler:**  
  A program that runs on an external computer connected to the ZCU102 via Ethernet. It allows the definition of various experiments and hardware classes (e.g., specific memory models), as well as instances of those classes. The scheduler manages the execution of experiments on these instances, delegating them either to the PS Software on the ZCU102 or to a microcontroller-based reference setup (described next).  
  It also collects the resulting measurement data, stores it persistently, and keeps track of the experiments executed for each hardware instance.

- **Microcontroller-Based Setup:**  
  An implementation running on an STM32F429 microcontroller with an integrated memory controller, capable of executing the same set of experiments as the ZCU102. However, this setup is constrained by the significantly lower clock frequency of its memory controller (120 MHz compared to 400 MHz on the FPGA). Communication with the test scheduler is established via a UART interface.

