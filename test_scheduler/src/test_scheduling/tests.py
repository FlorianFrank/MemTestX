import json
import time
from asyncio.log import logger

from db_handler import DBHandler
from definitions import Command
from network_handler import NetworkHandler, IPConfig
from serial_handler import SerialHandler, DEFAULT_BAUDRATE
from setup import Setup
from test_defines import TestTemplate, TestType
from test_scheduler import TestScheduler, Test

DB_NAME = "memories.db"
IP_SUFFIX = "192.168.178"  # "132.231.14"
PORT_SEND = 5024
PORT_RECV = 5023


class SampleTests:
    @staticmethod
    def test_network_connection(network_handler: NetworkHandler, ip_config: IPConfig) -> bool:
        network_handler.send_config(ip_config=ip_config, cmd=Command.CMD_IDN)
        time.sleep(1)
        if network_handler.is_response_received():
            logger.info(f"test_network_connection returned response: {network_handler.get_response()}")
        return True

    @staticmethod
    def send_sample_test(network_handler: NetworkHandler, ip_config: IPConfig) -> bool:
        with open('config_files/memory_configs/FRAM_Cypress_FM22L16_55_TG.json', 'r') as config_file:
            config = json.load(config_file)
            network_handler.send_config(ip_config=ip_config, cmd=Command.CMD_START_MEASUREMENT, cfg=config)
        return True

    @staticmethod
    def sample_test_execution_localhost():
        network_handler = Setup.setup_network('localhost', PORT_SEND, PORT_RECV)
        #db_handler = Setup.create_initial_db_scheme(DB_NAME, True)
        #memory_inst_dict = {'test_ctr': 0, 'label': 'FRAM_CYPRESS_1', 'comment': 'Nix',
         #                   'memory_type_label': 'MRAM_Everspin_MR4A08BUYS45'}
        #db_handler.add_memory_instance(memory_inst_dict)

        zync_ip_config = IPConfig(ip="localhost", port=PORT_SEND)
        test_scheduler = TestScheduler(time_between_tests_in_ms=1000, comm_interface=network_handler,
                                       server_ip=zync_ip_config)

        # temp1 = TestTemplate(type=TestType.RELIABLE, start_ts=0, end_ts=0,
        #                    memory_type_name='FRAM_Cypress_FM22L16_55_TG', parameters={'tACWrite': -2})
        temp2 = TestTemplate(type=TestType.ROW_HAMMERING, start_ts=0, end_ts=0,
                             memory_type_name='FRAM_Cypress_FM22L16_55_TG', parameters={'tWaitBetweenHammering': 100,
                                                                                        'hammeringIterations': 2,
                                                                                        'hammeringDistance': 5},
                             comment="NULL")

        # ADD sample tests
        # test_scheduler.add_test(
        #    Test(memory_label="FRAM_CYPRESS_1", test_template=temp1))
        test_scheduler.add_test(
            Test(memory_label="FRAM_CYPRESS_1", test_template=temp2, board="STM32F429-DISC1"))

        test_scheduler.run_scheduler_loop()

    @staticmethod
    def add_fram_rohm_latency_tests(memory_name: str, test_scheduler: TestScheduler, init_value: int, puf_value: int):
        timing_values = [+4, 0, -2, -6, -10, -13, -16, -20, -23, -26]
        #timing_values = [-4, -8,-12,-14, -18, -20, -24, -28, -31, -34, -38, -41, -44]
        measured_timing_we = [83.7, 75.9, 67.2, 59.2, 50.3, 41.6, 33.8, 24.6, 16.7, 4.7]
        measured_timing_oe = [83.7, 75.9, 59.2, 50.5, 41.7, 34.5, 25.6, 17.7, 8.9]

        test_template = TestTemplate(
            type=TestType.RELIABLE,
            start_ts=0,
            end_ts=0,
            memory_type_name='FRAM_Cypress_FM22L16_55_TG',
            parameters={'init_value': init_value, 'puf_value': puf_value},
            comment=(
                'WE width measured with 75.9 ns CE is aligned with WE at the first flank, '
                'while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz.'
            )
        )
        test_scheduler.add_test(Test(memory_label=memory_name, test_template=test_template, board="STM32F429-DISC1"))

        for timing_osc, timing_value in zip(measured_timing_oe, timing_values):
            test_template = TestTemplate(
                type=TestType.READ_LATENCY,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Cypress_FM22L16_55_TG',
                parameters={'tPRC': timing_value, 'init_value': init_value, 'puf_value': puf_value},
                comment=(
                    f'OE width measured with {timing_osc} ns CE is aligned with OE at the first flank, '
                    f'while CE has no offset. STM32 was configured with PLL = 120 Hz.'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_name, test_template=test_template, board="STM32F429-DISC1"))

        for timing_osc, timing_value in zip(measured_timing_we, timing_values):
            test_template = TestTemplate(
                type=TestType.WRITE_LATENCY,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Cypress_FM22L16_55_TG',
                parameters={'tPWDWrite': timing_value, 'init_value': init_value, 'puf_value': puf_value},
                comment=(
                    f'WE width measured with {timing_osc} ns CE is aligned with WE at the first flank, '
                    f'while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz.'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_name, test_template=test_template, board="STM32F429-DISC1"))

    @staticmethod
    def add_mram_35_latency_tests(memory_name: str, test_scheduler: TestScheduler, init_value: int, puf_value: int):
        timing_values = [0, -3, -7, -10, -13]
        # timing_values = [-4, -8,-12,-14, -18, -20, -24, -28, -31, -34, -38, -41, -44]
        measured_timing_we = [ 41.6, 33.8, 24.6, 16.7, 4.7]
        measured_timing_oe = [41.7, 34.5, 25.6, 17.7, 8.9]

        test_template = TestTemplate(
            type=TestType.RELIABLE,
            start_ts=0,
            end_ts=0,
            memory_type_name='MRAM_Everspin_MR4A08BCMA35',
            parameters={'init_value': init_value, 'puf_value': puf_value},
            comment=(
                'WE width measured with 75.9 ns CE is aligned with WE at the first flank, '
                'while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz.'
            )
        )
        test_scheduler.add_test(Test(memory_label=memory_name, test_template=test_template, board="STM32F429-DISC1"))

        for timing_osc, timing_value in zip(measured_timing_oe, timing_values):
            test_template = TestTemplate(
                type=TestType.READ_LATENCY,
                start_ts=0,
                end_ts=0,
                memory_type_name='MRAM_Everspin_MR4A08BCMA35',
                parameters={'tPRC': timing_value, 'init_value': init_value, 'puf_value': puf_value},
                comment=(
                    f'OE width measured with {timing_osc} ns CE is aligned with OE at the first flank, '
                    f'while CE has no offset. STM32 was configured with PLL = 120 Hz.'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_name, test_template=test_template, board="STM32F429-DISC1"))

        for timing_osc, timing_value in zip(measured_timing_we, timing_values):
            test_template = TestTemplate(
                type=TestType.WRITE_LATENCY,
                start_ts=0,
                end_ts=0,
                memory_type_name='MRAM_Everspin_MR4A08BCMA35',
                parameters={'tPWDWrite': timing_value, 'init_value': init_value, 'puf_value': puf_value},
                comment=(
                    f'WE width measured with {timing_osc} ns CE is aligned with WE at the first flank, '
                    f'while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz.'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_name, test_template=test_template, board="STM32F429-DISC1"))
    @staticmethod
    def add_voltage_tests(test_scheduler, memory_label, init_value, puf_value):
        for i in  range(0, 30):
            test_template = TestTemplate(
                type=TestType.VOLTAGE_READ,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Fujitsu_MB85R1001ANC_GE1',
             #   parameters={'init_value': 0x5555, 'puf_value': 0xaaaa, 'current_change': -(0.001 * i)},
                parameters={'init_value': init_value, 'puf_value': puf_value, 'voltage_change': -(0.1 * i)},
                comment=(
                    f'Voltage {0.02 - round((i * 0.1), 3)} using level shifter which also controls WE, CE1, CE2 and OE'
                )
            )
            test_scheduler.add_test(Test(memory_label=memory_label, test_template=test_template, board="STM32F429-DISC1"))

        for i in range(0, 30):
            test_template = TestTemplate(
                type=TestType.VOLTAGE_WRITE,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Fujitsu_MB85R1001ANC_GE1',
                #   parameters={'init_value': 0x5555, 'puf_value': 0xaaaa, 'current_change': -(0.001 * i)},
                parameters={'init_value': init_value, 'puf_value': puf_value, 'voltage_change': -(0.1 * i)},
                comment=(
                    f'Voltage {0.02 - round((i * 0.1), 3)} using level shifter which also controls WE, CE1, CE2 and OE'                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_label, test_template=test_template, board="STM32F429-DISC1"))


        """for i in range(0, 15):
            test_template = TestTemplate(
                type=TestType.VOLTAGE_READ,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Fujitsu_MB85R1001ANC_GE1',
                parameters={'init_value': init_value, 'puf_value': puf_value, 'current_change': -(0.001 * i)},
                #parameters={'init_value': 0x5555, 'puf_value': 0xaaaa, 'voltage_change': -(0.1 * i)},
                comment=(
                    f'Voltage {0.02 - round((i * 0.001), 3)}'
                )
            )
            test_scheduler.add_test(Test(memory_label=memory_label, test_template=test_template, board="STM32F429-DISC1"))

        for i in range(0, 15):
            test_template = TestTemplate(
                type=TestType.VOLTAGE_WRITE,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Fujitsu_MB85R1001ANC_GE1',
                parameters={'init_value': init_value, 'puf_value': puf_value, 'current_change': -(0.001 * i)},
                #parameters={'init_value': 0x5555, 'puf_value': 0xaaaa, 'voltage_change': -(0.1 * i)},
                comment=(
                    f'current {0.02 - round((i * 0.001), 3)}'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_label, test_template=test_template, board="STM32F429-DISC1"))"""

    @staticmethod
    def sample_test_execution_zync():
        srv_ip = NetworkHandler.detect_network_interface_with_suffix(IP_SUFFIX)
        logger.info(f"Detected server ip: {srv_ip} -> Setup Network")

        network_handler = Setup.setup_network(ip_address=srv_ip, port_send=PORT_SEND, port_recv=PORT_RECV)
        #db_handler = Setup.create_initial_db_scheme(DB_NAME, True)
        #add_all_memory_instances_to_db(db_handler, logger)

        db_handler = DBHandler(DB_NAME)
        db_handler.initialize()

        # TODO use either one or the other
        zync_ip_config = IPConfig(ip="132.231.14.92", port=PORT_SEND)
        serial_ports = SerialHandler.find_usbmodem_ports()
        logger.info(f"Detected serial ports {serial_ports} -> select first from list")
        serial_interface = SerialHandler(serial_ports[0], DEFAULT_BAUDRATE)

        test_scheduler = TestScheduler(test_queue=None, time_between_tests_in_ms=200, server_ip=zync_ip_config,
                                       comm_interface=serial_interface)

        for i in range(3):
            SampleTests.add_mram_35_latency_tests("MrE35.3", test_scheduler, 0x5555, 0xaaaa)

        for i in range(4):
            SampleTests.add_mram_35_latency_tests("MrE35.3", test_scheduler, 0xffff, 0x0000)
        test_scheduler.run_scheduler_loop()


if __name__ == '__main__':
    SampleTests.sample_test_execution_localhost()
