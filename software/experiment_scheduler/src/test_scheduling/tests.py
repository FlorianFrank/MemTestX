import json
import time
from asyncio.log import logger

from db_handler import DBHandler
from definitions import Command
from memory_instance_handler import add_all_memory_instances_to_db
from network_handler import NetworkHandler, IPConfig
from serial_handler import SerialHandler, DEFAULT_BAUDRATE
from setup import Setup
from test_defines import TestTemplate, TestType
from test_scheduler import TestScheduler, Test

DB_NAME = "memories.db"
IP_SUFFIX = "132.231.14"  # "132.231.14"
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
            Test(memory_label="FRAM_CYPRESS_1", test_template=temp2, board="Ultrascale ZCU102"))

        test_scheduler.run_scheduler_loop()

    @staticmethod
    def add_fram_rohm_row_hammering_test(memory_name: str, test_scheduler: TestScheduler, init_value: int,
                                         puf_value: int):

        hammering_distances = [64, 128, 256, 512, 1024]
        hammering_iterations = [100, 1000, 10000, 100000] # , 1000000
        #hammering_iterations = [100000] #100000]  # , 1000000

        test_template = TestTemplate(
            type=TestType.RELIABLE,
            start_ts=0,
            end_ts=0,
            memory_type_name='FRAM_Rohm_MR48V256C',
            parameters={'init_value': 0x5555, 'puf_value': 0xaaaa},
            comment=(
                'WE width measured with 75.9 ns CE is aligned with WE at the first flank, '
                'while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz.'
            )
        )

        for i in range(10):
            test_scheduler.add_test(Test(memory_label=memory_name, test_template=test_template, board="Ultrascale ZCU102"))

        for distance in hammering_distances:
            for iterations in hammering_iterations:
                test_template = TestTemplate(type=TestType.ROW_HAMMERING, start_ts=0, end_ts=0,
                                             memory_type_name='FRAM_Rohm_MR48V256C',
                                             parameters={'tWaitBetweenHammering': 1,
                                                         'hammeringIterations': iterations,
                                                         'hammeringDistance': distance, 'init_value': puf_value,
                                                         'puf_value': init_value},
                                             comment=f"Row hammering with hammering distance {distance} and {iterations} under default timing")
                test_scheduler.add_test(
                    Test(memory_label=memory_name, test_template=test_template, board="Ultrascale ZCU102"))

    @staticmethod
    def add_fram_rohm_latency_tests(memory_name: str, test_scheduler: TestScheduler, init_value: int, puf_value: int):
        timing_values = [-x for x in range(0, 1, 1)]
        measured_timing_we = [30*2.5] + [(30-x)*2.5 for x in range(0,20,1)]
        measured_timing_oe = [30*2.5] + [(30-x)*2.5 for x in range(0,20,1)]
        for i in range(100):
            test_template = TestTemplate(
              type=TestType.RELIABLE,
               start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Rohm_MR48V256C',
                parameters={'init_value': init_value, 'puf_value': puf_value},
                comment=(
                    'WE width measured with 75.9 ns CE is aligned with WE at the first flank, '
                    'while CE has an offset of 8.8 ns at the second flank. STM32 was configured with PLL = 120 Hz.'
                )
            )
            test_scheduler.add_test(Test(memory_label=memory_name, test_template=test_template, board="Ultrascale ZCU102"))

        for timing_osc, timing_value in zip(measured_timing_oe, timing_values):
            test_template = TestTemplate(
                type=TestType.READ_LATENCY,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Rohm_MR48V256C',
                parameters={'tOEDRead': timing_value, 'init_value': puf_value, 'puf_value':  init_value},
                comment=(
                   f'Configures with CE, OE and WE of equal length on a ZCU102 using level shifters '
                   f'Data lines are connected via J3 Pin. Using Ultrascale+ in steps of 2.5 ns'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_name, test_template=test_template, board="Ultrascale ZCU102"))

        for timing_osc, timing_value in zip(measured_timing_we, timing_values):
            test_template = TestTemplate(
                type=TestType.WRITE_LATENCY,
                start_ts=0,
                end_ts=0,
                memory_type_name='FRAM_Rohm_MR48V256C',
                parameters={'tDSWrite': timing_value, 'init_value': init_value, 'puf_value': puf_value},
                comment=(
                    f'WE width measured with {timing_osc} ns CE is aligned with WE at the first and second flank, '
                    f'Data lines are connected via J3 Pin. Using Ultrascale+ in steps of 2.5 ns'
                )
            )
            test_scheduler.add_test(
                Test(memory_label=memory_name, test_template=test_template, board="Ultrascale ZCU102"))

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
        #serial_ports = SerialHandler.find_usbmodem_ports()
        #logger.info(f"Detected serial ports {serial_ports} -> select first from list")
        #serial_interface = SerialHandler(serial_ports[0], DEFAULT_BAUDRATE)

        test_scheduler = TestScheduler(test_queue=None, time_between_tests_in_ms=200, server_ip=zync_ip_config,
                                       comm_interface=network_handler)


        for i in range(30):
            SampleTests.add_fram_rohm_row_hammering_test("FeLa2", test_scheduler, 0x5555,  0xaaaa)

        #for i in range(5):
         #  SampleTests.add_fram_rohm_latency_tests("FeLa3", test_scheduler, 0x5555,  0xaaaa)

        #for i in range(5):
         #  SampleTests.add_fram_rohm_latency_tests("FeLa6", test_scheduler,0x5555, 0xaaaa)

        #for i in range(5):
         #   SampleTests.add_fram_rohm_latency_tests("FeLa6", test_scheduler, 0xffff,  0x0000)
        test_scheduler.run_scheduler_loop()


if __name__ == '__main__':
    SampleTests.sample_test_execution_localhost()
