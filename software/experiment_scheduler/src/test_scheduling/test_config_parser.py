import logging
from itertools import product

import numpy as np
import yaml

from test_defines import string_to_test_type, TestTemplate, Test
from test_scheduler import TestScheduler


class TestConfigParser:
    """
    Parses YAML configuration files defining test setups and parameters,
    converts them into TestTemplate and Test objects, and adds them to the TestScheduler.
    """

    def __init__(self, config_file: str):
        self._config_file = config_file
        self._test_list = []
        self._test_list = []
        self._platform = ""

    def initialize_test_scheduler(self, scheduler: TestScheduler):
        logging.info(f"Add {len(self._test_list)} experiments to scheduler")
        for test in self._test_list:
            scheduler.add_test(test)

    def get_platform(self):
        return self._platform

    @staticmethod
    def parse_parameter(parameters: dict) -> list[dict]:
        """
        Parse test parameters, separating static and range values.

        Static parameters e.g. the
        Static parameters are single fixed values.

        This function generates all possible combinations of dynamic parameter values
        using Cartesian product expansion.

        Args:
            parameters (dict): Dictionary containing static and/or dynamic parameter definitions.

        Returns:
            list[dict]: A list of parameter dictionaries, each representing one combination of values.
        """
        static_values = dict()
        range_values = dict()
        for key, value in parameters.items():
            if isinstance(value, dict):
                start = value['range_start']
                stop = value['range_end']
                step = value['step_size'] if value['range_end'] > value['range_start'] else -value['step_size']
                range_values.update({key: [float(x) for x in list(np.arange(start, stop, step))]})
            else:
                static_values.update({key: value})

        parameter_list = [
            dict(zip(range_values.keys(), values))
            for values in product(*range_values.values())
        ]
        for c in parameter_list:
            c.update(static_values)
        return parameter_list

    def parse_experiment(self, experiment_config: dict, memory_type: str) -> list[TestTemplate]:
        test_type = string_to_test_type(experiment_config["type"])
        comment = experiment_config['comment']
        parameter_list = self.parse_parameter(experiment_config['parameters'])

        return [TestTemplate(
            type=test_type,
            start_ts=0,  # will be filled during scheduling
            end_ts=0,  # will be filled during scheduling
            memory_type_name=memory_type,
            comment=comment,
            parameters=param
        ) for param in parameter_list]

    def parse_config(self):
        try:
            with open(self._config_file, 'r') as config_file:
                parsed_config = yaml.safe_load(config_file.read())

                self._platform = parsed_config['test_collection']['platform']
                iterations = parsed_config['test_collection']['iterations']
                memory_type = parsed_config['test_collection']['memory_type']
                memory_instance = parsed_config['test_collection']['memory_instance']
                experiments = parsed_config['test_collection']['experiments']

                for iteration in range(iterations):
                    for experiment in experiments:
                        for template in self.parse_experiment(experiment['experiment'], memory_type):
                            logging.debug(f"Register experiment: {template}")
                            self._test_list.append(Test(memory_label=memory_instance, test_template=template,
                                                        board=self._platform))

        except Exception as err:
            logging.error(f"Could not parse config, returned with error {err}")
