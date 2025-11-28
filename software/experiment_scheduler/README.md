# Experiment Scheduler

In this folder you will find a program capable of scheduling experiments either on the Xilinx ZCU102 or the STM32F429.  
Furthermore, it allows the persistent storage of measurement data as CSV files and the storage of metadata in a SQLite database.

<center>
<img src="../../doc/figures/experiment_scheduler.svg" style="width: 100%;" alt="Experiment Scheduler">
</center>

Overall, this implementation provides the following functionality:

- Definition of experiments in a YAML-based format with different parameters and parameter ranges.  
- Persistent storage and management of different types of memories and their parameters, which can be imported from JSON files.  
- Storage of different test instances and keeping track of the number of experiments.  
- Scheduling of experiments either to an AMD ZCU102 using an Ethernet interface or to an STM32F429 using UART.  
- Persistent storage of measurement data in CSV files, with their metadata stored in a database.  
- Interconnection to measurement devices using our self-implemented instrument control library, specifically the connection 
  with an SPD1305X power supply in order to perform voltage variation tests.

## Configuration

The program can be customized through multiple configuration files.  
In the `config_files` directory, the configuration of the memory models under test can be found in the `memory_configs` subfolder. For example:


```json
{
 "name": "FRAM_Cypress_FM22L16_55_TG",
  "manufacturer": "Cypress",
  "technology": "FRAM",
  "model": "FM22L16_55_TG",
  "interface_type": "parallel",
  "address_width": 18,
  "data_width": 16,
  "min_addr": 0,
  "max_addr": 200,
  "voltage": 3,
  "current": 0.2,
  "comment": "Also configurable as 8 bit using UB and LB"
}
```

The timing parameters can be found in a dedicated folder `test_config`. An example of such as file is listed below:

```json
{
  "name": "FRAM_Cypress_FM22L16_55_TG",
  "ceDrivenWrite": true,
  "ceDrivenRead": true,

  "tWaitAfterInit": 18,
  "tNextRead":  100000,
  "tStartWrite": 3,
  "tNextWrite": 4,
  "tACWrite": 5,
  "tASWrite": 6,
  "tAHWrite": 7,
  "tPWDWrite": 8,
  "tDSWrite": 9,
  "tDHWrite": 10,
  "tStartRead": 10,
  "tASRead": 9,
  "tAHRead": 8,
  "tOEDRead": 7,
  "tPRCRead": 6,
  "tCEOEEnableRead": 5,
  "tCEOEDisableRead": 4,
  "comment": "Nothing to report"
}
```
These timing parameters have a granularity of 2.5 ns.  
For example, `tStartWrite: 3` corresponds to an actual timing value of `2.5 * 3 + <delay of lvl shifters>`.

For more information about the timing parameters, refer to the `hardware/fpga_design` directory, where you can find timing diagrams for all defined parameters.

> Note that `tNextRead` is set to a relatively large value. This is due to the fact that after each read operation, the measured value is sent to the CPU and then transmitted to this application.

Additional configuration files in this folder define the IP settings for the evaluation and measurement devices.

### Test Specification

Additional YAML files are provided in the `samples` folder, specifying sets of experiments to be executed on specific memory instances.  
A custom format is implemented to allow you to define your own tests, as shown in the following code example:

```yaml

test_collection:
    platform: "Ultrascale ZCU102"
    memory_type: FRAM_Rohm_MR48V256C
    memory_instance: FeLa2
    iterations: 10

    experiments:
      - experiment:
          type: reliable
          parameters:
            init_value: 0x55
            puf_value: 0xAA
          comment: "CE is aligned with WE at the first flank while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz."

      - experiment:
          type: readLatency
          parameters:
            init_value: 0xAA
            puf_value: 0x55
            tOEDRead:
              range_start: 75
              range_end: 27.5
              step_size: 2.5
          comment: "Configures with CE, OE and WE of equal length on a ZCU102 using level shifters Data lines are connected via J3 Pin. Using Ultrascale+ in steps of 2.5 ns" 
```

This example defines a test configuration for a memory type named **FRAM Rohm MR48V256C**, with the specific memory instance identified as **FeLa2**.  

In the **experiments** section, individual experiments can be defined in sequential order.  
In this example, the first experiment performs a reliable read and write operation on the memory, using an initial value of `0x55` and a PUF value of `0xAA`.  
Afterward, a `readLatencyTest` is executed, where all timing parameters remain unchanged except for `tOERead`.  
Here, explicit timing values or a range can be specified. In this case, dedicated experiments are generated for each timing value between **75 ns and 27.5 ns**, in **2.5 ns steps**, resulting in **19 individual experiments** executed sequentially.  

Thus, ten iterations of the reliability test and the nineteen read latency tests lead to a total of **200 individual experiments** automatically scheduled and performed.  
All parameters not explicitly specified in the configuration use their **default values**.

Further examples on how to define writeLatency or voltage variation tests are provided in the same folder.

## Setup

Similar to the other components of this project, we provide scripts to set up the system and run the implementation.  
To create a virtual Python environment, install all dependencies, and initialize the database (including storing all memory class and instance definitions found in the `config_files` directory) simply run the following commands:

```bash
./setup_db.sh
```

> ️ ⚠️ Calling this script will delete the content of your sqlite database. Do not call this script again after initialization or backup your database first.


## Execute the Program

In order to start the scheduler run the following script:

```bash
./run_all.sh -config_file=<Experiment Script>
```
e.g. 

```bash
./run_all.sh -config_file=samples/sample_experiment_write_latency_fram_lapis.yaml
```

You can also run the python application directly by calling

```bash
python3 main.sh -config_file=samples/sample_experiment_write_latency_fram_lapis.yaml
```

This script accepts the following command-line parameters:

- **-config_file=<config_file.yaml>**  
  Specifies the test configuration file to be used.

- **-init_db_scheme**  
  Creates a new database schema, parses all memory configurations found in the `config_files` folder, and inserts them into the database.  
  > ⚠️ **Warning:** This option will drop (delete) the entire database before reinitialization.

- **-refresh_memories**  
  Adds new memory modules by parsing any files placed in the `config_files` folder.  
  Only new modules and parameters not already present in the database will be added automatically.

## Evaluation 

All evaluation functions and files can be found in the evaluation folder. 
This directory also includes a Jupyter notebook that demonstrates how to evaluate 
measurement data collected by the scheduler.
> All descriptions can be found directly within the notebook.


## Tools 

Additional tools are available in the `tools` folder.
Currently, this includes a **database merger tool,** which 
allows you to run multiple instances of the scheduler, 
each operating on a separate database. This tool can then 
merge the individual databases into a single combined dataset 
for analysis.

To run the tool, use the following command:

```bash 
python3 db_merger.py db1.db db2.db output.db
```

This command merges the entries from `db1.db` and `db2.db` and 
creates a new merged database named `output.db`.