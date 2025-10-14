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

### Components Description

The design uses the components listed by their schematic symbols.  
>Prices are based on 2025 data from common distributors, including Mouser and DigiKey or Reichelt.


| Ref.      | Type                        | Manufacturer      | Component Number     | Description                             | Unit Price | Qty | Total Price | Verified |
|-----------|-----------------------------|-----------------|-------------------|-----------------------------------------|------------|-----|-------------|----------|
| J8        | FMC Adapter                 | SAMTEC           | ASP-134488         | Connector between the FPGA J5 FMC adapter and the breakout board for Data Line D0 | 32 €       | 1   | 32 €        | ✅       |
| IC1 - IC6 | Dual-Supply Bus Transceiver | Texas Instruments | SN74AVC8T245PWG4 | Logic Level shifting using two reference power rails. | 1.32 €     | 6   | 7.92 €      | ✅       |
| C1 - C12  | Capacitors                  | KEMET             | C0805C104K5RAC7411 | 0.1 µF, 50 V DC, decoupling capacitors for bus transceivers (VCCA/VCCB inputs) | 0.10 €     | 12  | 1.20 €      | ✅       |
| P1, P2    | Pin Headers 2×32            | MPE               | 087-2-064-0-S-XS0-1260 | 2×32 straight pin headers, 2.54 mm pitch, for connecting the memory module | 1.10 €     | 2   | 2.20 €      | ✅       |
| J7        | Pin Headers Power Supply     | Würth Elektronik  | 61300621121        | 2×3 straight pin headers, 2.54 mm pitch, to access the power supply connector | 0.32 €     | 1   | 0.32 €      | ✅       |
| J10       | Pin Headers Ground Selectors | Würth Elektronik  | 61301621121        | 2×8 straight pin headers, 2.54 mm pitch, to access ground connections | 0.81 €     | 1   | 0.81 €      | ✅       |
| J1 - J5   | Pin Headers Ground Selectors | Amphenol Commercial Products | G800NA306018EU | 1×2 straight pin headers, 2.54 mm pitch, for single ground connectors | 0.09 €     | 5   | 0.45 €      | ✅       |
| J9        | Debug Pin Header             | Würth Elektronik  | 61300311121        | 1×3 straight pin headers, 2.54 mm pitch, for debug pins | 0.10 €     | 1   | 0.10 €      | ✅       |

The board was manufactured as a four-layer PCB with a standard HASL finish (TG150), leaded configuration, 2 mm thickness, 4 mil/4 mil track spacing, and a minimum hole size of 0.2 mm.  

A batch of five pieces was priced at approximately 130 €, including shipping, from [PCBgogo](https://www.pcbgogo.com).

The total cost to manufacture the complete PCB was approximately **175 €**, excluding the cost of additional materials required for soldering.

### Pinout Description

This section presents the different pinout descriptions based on the components uniquely identified within the design by their symbol names.

#### FMC Adapter (Symbol Name: J8)

> ⚠️ Verify that the pinout matches the constraints defined in your FPGA hardware design constraints file.

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   | Verified |
|------|-------------|-----------------|---------------|------------------|----------|
| C10  | LVCMOS18    | IC1             | A1            |  Data Line D0    |    ✅    |
| C11  | LVCMOS18    | IC1             | A2            |  Data Line D1    |    ✅    |
| C14  | LVCMOS18    | IC1             | A3            |  Data Line D2    |    ✅    |
| C15  | LVCMOS18    | IC1             | A4            |  Data Line D3    |    ✅    |
| C18  | LVCMOS18    | IC1             | A5            |  Data Line D4    |    ✅    |
| C19  | LVCMOS18    | IC1             | A6            |  Data Line D5    |    ✅    |
| C22  | LVCMOS18    | IC1             | A7            |  Data Line D6    |    ✅    |
| C23  | LVCMOS18    | IC1             | A8            |  Data Line D7    |    ✅    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   | Verfied  |
|------|-------------|-----------------|---------------|------------------|----------|
| C26  | LVCMOS18    | IC2             | A1            | Data Line D8     |    ✅    |
| C27  | LVCMOS18    | IC2             | A2            | Data Line D9     |    ✅    |
| D8   | LVCMOS18    | IC2             | A3            | Data Line D10    |    ✅    |
| D9   | LVCMOS18    | IC2             | A4            | Data Line D11    |    ✅    |
| D11  | LVCMOS18    | IC2             | A5            | Data Line D12    |    ✅    |
| D12  | LVCMOS18    | IC2             | A6            | Data Line D13    |    ✅    |
| D14  | LVCMOS18    | IC2             | A7            | Data Line D14    |    ✅    |
| D15  | LVCMOS18    | IC2             | A8            | Data Line D15    |    ✅    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   | Verfied  |
|------|-------------|-----------------|---------------|------------------|----------|
| D17  | LVCMOS18    | IC4             | A1            | Address Line A0  |    ✅    |
| D18  | LVCMOS18    | IC4             | A2            | Address Line A1  |    ✅    |
| D20  | LVCMOS18    | IC4             | A3            | Address Line A2  |    ✅    |
| D21  | LVCMOS18    | IC4             | A4            | Address Line A3  |    ✅    |
| D23  | LVCMOS18    | IC4             | A5            | Address Line A4  |    ✅    |
| D24  | LVCMOS18    | IC4             | A6            | Address Line A5  |    ✅    |
| D26  | LVCMOS18    | IC4             | A7            | Address Line A5  |    ✅    |
| D27  | LVCMOS18    | IC4             | A8            | Address Line A7  |    ✅    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   | Verified |
|------|-------------|-----------------|---------------|------------------|----------|
| G6   | LVCMOS18    | IC5             | A1            | Address Line A8  |    ✅    |
| G7   | LVCMOS18    | IC5             | A2            | Address Line A9  |    ✅    |
| G9   | LVCMOS18    | IC5             | A3            | Address Line A10 |    ✅    |
| G10  | LVCMOS18    | IC5             | A4            | Address Line A11 |    ✅    |
| G12  | LVCMOS18    | IC5             | A5            | Address Line A12 |    ✅    |
| G13  | LVCMOS18    | IC5             | A6            | Address Line A13 |    ✅    |
| G15  | LVCMOS18    | IC5             | A7            | Address Line A14 |    ✅    |
| G16  | LVCMOS18    | IC5             | A8            | Address Line A15 |    ✅    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description   | Verified |
|------|-------------|-----------------|---------------|------------------|----------|
| G18  | LVCMOS18    | IC6             | A1            | Address Line A16 |    ✅    |
| G19  | LVCMOS18    | IC6             | A2            | Address Line A17 |    ✅    |
| G21  | LVCMOS18    | IC6             | A3            | Address Line A18 |    ✅    |
| G22  | LVCMOS18    | IC6             | A4            | Address Line A19 |    ✅    |
| G24  | LVCMOS18    | IC6             | A5            | Address Line A20 |    ✅    |
| G25  | LVCMOS18    | IC6             | A6            | Address Line A21 |    ✅    |
| G27  | LVCMOS18    | IC6             | A7            | Address Line A22 |    ✅    |
| G28  | LVCMOS18    | IC6             | A8            | Address Line A23 |    ✅    |

| Pin  | I/O Standard | Mapping Component | Component Pin | Description         | Verified |
|------|-------------|-----------------|---------------|------------------------|----------|
| G30  | LVCMOS18    | IC3             | A1            | Output Enable !OE      |    ✅    |
| G31  | LVCMOS18    | IC3             | A2            | Write Enable !WE       |    ✅    |
| G33  | LVCMOS18    | IC3             | A3            | Chip Enable !CE        |    ✅    |
| G34  | LVCMOS18    | IC3             | A4            | Lower Byte Select !LB  |    ✅    |
| G36  | LVCMOS18    | IC3             | A5            | Upper Byte Select !UB  |    ✅    |
| G37  | LVCMOS18    | IC3             | A6            | Sleep Pin !ZZ          |    ✅    |

