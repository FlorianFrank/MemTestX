## Software Components

This folder contains all software components required to execute the memory evaluation implementation. It is composed of three main parts:

### PS Software

The firmware runs on the ZCU102’s Cortex-A53 processor. It provides an interface to receive commands via Ethernet from the test scheduler and is capable of parsing the incoming data. On the other hand, it manages the interaction with the software running on the Programmable Logic (PL). The firmware transmits the Ethernet-received commands to the PL, monitors execution through the AXI interface, and collects the resulting measurement data, which it then forwards back to the scheduler via Ethernet.

### Experiment Scheduler

A Python-based program that can run on any computer capable of communicating with the ZCU102 via Ethernet. It allows users to define experiments, which are managed and executed by an internal scheduler. The program forwards commands either to the microcontroller-based setup (described below) or directly to the ZCU102. It also receives measurement data, which it stores persistently both in a database and as files, enriched with metadata such as memory type, PUF values, and the number of experiments performed on each memory device.

### Memory Evaluator ZCU102

A reference implementation using a ZCU102 that supports the same set of experiments as the main ZCU102 setup. However, due to the significantly lower operating frequency of its integrated memory controller, timing adjustments can only be made with lower granularity. Additionally, the number of timing parameters that can be modified is limited.