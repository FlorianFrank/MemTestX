import json
import os.path
import time
from typing import Optional
import pathlib

from db_handler import logger
from src.py_instrument_control_lib.device_base.DeviceConfigs import TCPDeviceConfig
from src.py_instrument_control_lib.device_types.PowerSupply import PSMode, PSChannel
from src.py_instrument_control_lib.devices.SPD1305X import SPD1305X


class PowerSupplyWrapper:
    def __init__(self):
        self._configuration = None
        self._dev_config = None
        self._measure_device: Optional[SPD1305X] = None

    def initialize(self):
        with open(os.path.join(pathlib.Path(__file__).parent.resolve(), '..', '..', 'config_files',
                               'measure_device.json'), "r") as config_file:
            self._configuration = json.loads(config_file.read())

        logger.info(
            f"Setup SPD1305X with parameters {self._configuration['ip_addr_power_supply']}:{self._configuration['port_power_supply']} Timeout {self._configuration['timeout_power_supply']}")
        self._dev_config = TCPDeviceConfig(ip=self._configuration['ip_addr_power_supply'],
                                           port=self._configuration['port_power_supply'],
                                           timeout=self._configuration['timeout_power_supply'])
        self._measure_device = SPD1305X(self._dev_config, requires_newline=False)
        self._measure_device.connect()

    def power_supply_default_settings(self, default_current: float, default_voltage: float) -> bool:
        logger.info(f"Make sure channel 1 is turned off")
        self._measure_device.toggle(PSChannel.CHANNEL_1, False)
        time.sleep(0.2)
        logger.info(f"Set SPD1305X in two wire mode")
        self._measure_device.set_mode(PSMode.W2, True)
        time.sleep(0.2)
        logger.info(f"Limit current to {default_current}")
        self._measure_device.set_current(PSChannel.CHANNEL_1, round(default_current, 3))
        logger.info(f"Set Voltage to {default_voltage}")
        time.sleep(0.2)
        self._measure_device.set_voltage(PSChannel.CHANNEL_1, round(default_voltage, 3))
        time.sleep(0.2)
        logger.info(f"Verify settings")
        default_voltage = 0
        ret_voltage = 0
        time_out = False
        for i in range(4):
            if time_out or i == 0:
                time_out = False
                try:
                    ret_voltage = self._measure_device.get_voltage(PSChannel.CHANNEL_1)
                except TimeoutError:
                    logger.error(f"Timeout occurred try again")
                    time_out = True
                    time.sleep(i + 1)
                if not time_out:
                    if abs(ret_voltage) - self._configuration['max_deviation_volts'] < default_voltage < abs(
                            ret_voltage) + self._configuration['max_deviation_volts']:
                        logger.info(f"Voltage of {default_voltage} verified")
                    else:
                        logger.error(f"Voltage could not be set {ret_voltage} != {default_voltage}!")
                        return False
        time.sleep(0.2)
        ret_current = 0
        time_out = False
        for i in range(4):
            if time_out or i == 0:
                time_out = False
            try:
                ret_current = self._measure_device.get_current(PSChannel.CHANNEL_1)
            except TimeoutError:
                logger.error(f"Timeout occurred try again -> sleep for {i + 1} seconds")
                time_out = True
                time.sleep(i + 1)
            if not time_out:
                if abs(ret_current) - self._configuration['max_deviation_current'] < default_current < abs(
                        ret_current) + self._configuration['max_deviation_current']:
                    logger.info(f"Current of {default_voltage} verified")
                else:
                    logger.error(f"Current could not be set {ret_current} != {default_current}!")
                    return False
        time.sleep(0.2)
        system_state = self._measure_device.get_system_status()
        if not system_state['output']:
            if system_state['wire_mode'] == PSMode.W2:
                if not system_state['timer']:
                    if system_state['display'] == 'digital_display':
                        logger.error(f"System status verification successful")
                        return True
                    else:
                        logger.error(f"Display not set in 'digital_display' mode")
                        return False
                else:
                    logger.error(f"Timer is enabled!")
                    return False
            else:
                logger.error(f"Wire mode not set to W2")
                return False
        else:
            logger.error(f"Output enabled!")

    def change_voltage(self, voltage: float, turn_on=True) -> bool:
        logger.info(f"Set Voltage to {voltage}")
        self._measure_device.toggle(PSChannel.CHANNEL_1, False)
        time.sleep(0.2)
        system_state = self._measure_device.get_system_status()
        if system_state['output']:
            logger.error(f"Device still enabled!")
            return False
        else:
            logger.info(f"Set voltage to {voltage}")
            self._measure_device.set_voltage(PSChannel.CHANNEL_1, round(voltage, 3))
            time.sleep(0.3)
            ret_voltage = 0
            time_out = False

            for i in range(4):
                if time_out or i == 0:
                    time_out = False
                    try:
                        ret_voltage = self._measure_device.get_voltage(PSChannel.CHANNEL_1)
                    except TimeoutError:
                        logger.error(f"Timeout occurred try again -> sleep for {i + 1} seconds")
                        time_out = True
                        time.sleep(i + 1)
                    if not time_out:
                        if abs(ret_voltage) - self._configuration['max_deviation_volts'] < voltage < abs(ret_voltage) + \
                                self._configuration['max_deviation_volts']:
                            logger.info(f"Voltage of {voltage} verified")
                            time.sleep(0.3)
                            logger.info(f"Enable voltage output")
                            if turn_on:
                                self._measure_device.toggle(PSChannel.CHANNEL_1, True)
                                time.sleep(0.3)
                                system_state = self._measure_device.get_system_status()
                                if system_state['output']:
                                    logger.info(f"Voltage is active")
                                    return True
                                else:
                                    logger.error(f"Could not enable voltage output!")
                        else:
                            logger.error(f"Voltage could not be set! ({ret_voltage} != {voltage})")
                            return False

    def change_current(self, current: float, turn_on=True) -> bool:
        logger.info(f"Set current to {current}")
        self._measure_device.toggle(PSChannel.CHANNEL_1, False)
        time.sleep(0.2)
        system_state = self._measure_device.get_system_status()
        if system_state['output']:
            logger.error(f"Device still enabled!")
            return False
        else:
            logger.info(f"Set current to {current}")
            self._measure_device.set_current(PSChannel.CHANNEL_1, round(current, 3))
            time.sleep(0.5)
            time_out = False
            ret_current = 0
            for i in range(4):
                if time_out or i == 0:
                    time_out = False
                    try:
                        ret_current = self._measure_device.get_current(PSChannel.CHANNEL_1)
                    except TimeoutError:
                        logger.error(f"Timeout occurred trie again -> sleep for {i + 1} seconds")
                        time_out = True
                        time.sleep(i + 1)
                    if not time_out:
                        if abs(ret_current) - self._configuration['max_deviation_current'] < current < abs(
                                ret_current) + self._configuration['max_deviation_current']:
                            logger.info(f"Current of {ret_current} verified")
                            time.sleep(0.3)
                            logger.info(f"Enable voltage output")
                            if turn_on:
                                self._measure_device.toggle(PSChannel.CHANNEL_1, True)
                                time.sleep(0.3)
                                system_state = self._measure_device.get_system_status()
                                if system_state['output']:
                                    logger.info(f"Current is active")
                                    return True
                                else:
                                    logger.error(f"Could not enable current output!")
                        else:
                            logger.error(f"Current could not be set {current} != {ret_current}!")
                            return False

    def turn_on(self):
        logger.info(f"Turn on power supply")
        self._measure_device.toggle(PSChannel.CHANNEL_1, True)

    def turn_off(self):
        logger.info(f"Turn off power supply")
        self._measure_device.toggle(PSChannel.CHANNEL_1, False)

    def disconnect(self):
        logger.info(f"Shut down channel 1")
        self._measure_device.toggle(PSChannel.CHANNEL_1, False)
        time.sleep(0.2)
        logger.info(f"Disconnect")
        self._measure_device.disconnect()
