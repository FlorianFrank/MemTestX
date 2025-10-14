# FMC Memory Adapter PCB

This folder contains all the design and manufacturing files for a Printed Circuit Board (PCB) adapter that enables interfacing various FRAM, MRAM, and ReRAM memory modules with the [AMD Zynq UltraScale+™ MPSoC ZCU102 Evaluation Kit](https://www.amd.com/en/products/adaptive-socs-and-fpgas/evaluation-boards/ek-u1-zcu102-g.html). 

The board is designed to connect to the FPGA Mezzanine Card (FMC) J5 connector on the ZCU102. It acts as a level-shifting bridge, converting the board’s output power rails (1.2 V, 1.5 V, or 1.8 V) to a standard CMOS 3.3 V logic level.

The PCB design is shown in the following figure:

<div style="text-align: center;">
  <img src="doc/figures/fmc_memory_adapter-brd.svg" style="width: 80%;" alt="FMC Memory Adapter Board">
</div>

The board uses an ANSI/VITA 57.1 compatible FMC adapter, shown at the bottom, and routes the logical signals, e.g., for the memory address bus, data bus, and control signals, to the two horizontal pin headers, which are compatible with the pinout of an STM32F429 (which served as the first evaluation platform).

To support different voltage levels and enable testing with various voltages, level shifters are used. They convert the input reference voltage (e.g., 1.8 V) into the voltage levels required by the memory module (e.g., CMOS 3.3 V). In this way, the power supply of the memory module can be decoupled, allowing tests with different reference voltages using external power supplies.

The board is constructed as a four-layer PCB, with the wires implementing logical levels primarily routed on the first two layers. These wires have equal line lengths to avoid potential glitches. The third layer is connected to ground, enhancing the board’s electromagnetic compatibility. On the backside, all ground connections and the power supply are routed using 0.8 mm traces.

The pin headers on the left side are used to connect different reference voltages and ground connections, as described later in the pinout description. The pin header in the middle is used for debugging purposes, allowing the output signals provided by the ZCU102 to be probed.

An additional connector is provided to supply a reference voltage to the FMC adapter’s VADJ_SENSE pin. This allows the VADJ_FMC power rail voltage to be selected using a resistor voltage divider.

### Pinout Description

The FMC has the following pinout description:  
> ⚠️ Verify that the pinout matches the constraints defined in your FPGA hardware design constraints file.

#### FMC Adapter (Symbol Name: J8)

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   |
|------|-------------|-----------------|---------------|------------------|
| C10  | LVCMOS18    | IC1             | A1            |  Data Line D0    |
| C11  | LVCMOS18    | IC1             | A2            |  Data Line D1    |
| C14  | LVCMOS18    | IC1             | A3            |  Data Line D2    |
| C15  | LVCMOS18    | IC1             | A4            |  Data Line D3    |
| C18  | LVCMOS18    | IC1             | A5            |  Data Line D4    |
| C19  | LVCMOS18    | IC1             | A6            |  Data Line D5    |
| C22  | LVCMOS18    | IC1             | A7            |  Data Line D6    |
| C23  | LVCMOS18    | IC1             | A8            |  Data Line D7    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   |
|------|-------------|-----------------|---------------|------------------|
| C26  | LVCMOS18    | IC2             | A1            | Data Line D8     |
| C27  | LVCMOS18    | IC2             | A2            | Data Line D9     |
| D8   | LVCMOS18    | IC2             | A3            | Data Line D10    |
| D9   | LVCMOS18    | IC2             | A4            | Data Line D11    |
| D11  | LVCMOS18    | IC2             | A5            | Data Line D12    |
| D12  | LVCMOS18    | IC2             | A6            | Data Line D13    |
| D14  | LVCMOS18    | IC2             | A7            | Data Line D14    |
| D15  | LVCMOS18    | IC2             | A8            | Data Line D15    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   |
|------|-------------|-----------------|---------------|------------------|
| D17  | LVCMOS18    | IC4             | A1            | Address Line A0  |
| D18  | LVCMOS18    | IC4             | A2            | Address Line A1  |
| D20  | LVCMOS18    | IC4             | A3            | Address Line A2  |
| D21  | LVCMOS18    | IC4             | A4            | Address Line A3  |
| D23  | LVCMOS18    | IC4             | A5            | Address Line A4  |
| D24  | LVCMOS18    | IC4             | A6            | Address Line A5  |
| D26  | LVCMOS18    | IC4             | A7            | Address Line A5  |
| D27  | LVCMOS18    | IC4             | A8            | Address Line A7  |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   |
|------|-------------|-----------------|---------------|------------------|
| G6   | LVCMOS18    | IC5             | A1            | Address Line A8  |
| G7   | LVCMOS18    | IC5             | A2            | Address Line A9  |
| G9   | LVCMOS18    | IC5             | A3            | Address Line A10 |
| G10  | LVCMOS18    | IC5             | A4            | Address Line A11 |
| G12  | LVCMOS18    | IC5             | A5            | Address Line A12 |
| G13  | LVCMOS18    | IC5             | A6            | Address Line A13 |
| G15  | LVCMOS18    | IC5             | A7            | Address Line A14 |
| G16  | LVCMOS18    | IC5             | A8            | Address Line A15 |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   |
|------|-------------|-----------------|---------------|------------------|
| G18  | LVCMOS18    | IC6             | A1            | Address Line A16 |
| G19  | LVCMOS18    | IC6             | A2            | Address Line A17 |
| G21  | LVCMOS18    | IC6             | A3            | Address Line A18 |
| G22  | LVCMOS18    | IC6             | A4            | Address Line A19 |
| G24  | LVCMOS18    | IC6             | A5            | Address Line A20 |
| G25  | LVCMOS18    | IC6             | A6            | Address Line A21 |
| G27  | LVCMOS18    | IC6             | A7            | Address Line A22 |
| G28  | LVCMOS18    | IC6             | A8            | Address Line A23 |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description         |
|------|-------------|-----------------|---------------|------------------------|
| G30  | LVCMOS18    | IC3             | A1            | Output Enable !OE      |
| G31  | LVCMOS18    | IC3             | A2            | Write Enable !WE       |
| G33  | LVCMOS18    | IC3             | A3            | Chip Enable !CE        |
| G34  | LVCMOS18    | IC3             | A4            | Lower Byte Select !LB  |
| G36  | LVCMOS18    | IC3             | A5            | Upper Byte Select !UB  |
| G37  | LVCMOS18    | IC3             | A6            | Sleep Pin !ZZ          |

