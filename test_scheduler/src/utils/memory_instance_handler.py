import logging

import logging

from db_handler import DBHandler


def add_all_memory_instances_to_db(db_handler: DBHandler, logger: logging.Logger) -> None:
    """
    Adds predefined memory instances to the database.

    This function inserts multiple memory instances of different types, such as FRAM, MRAM, and ReRAM,
    into the database using the provided DBHandler instance. Each memory instance is identified by a label,
    test counter (test_ctr), and additional comments.

    Memory types include:
      - FRAM_Rohm_MR48V256C
      - FRAM_Fujitsu_MB85R1001ANC_GE1
      - FRAM_Cypress_FM22L16_55_TG
      - MRAM_Everspin_MR4A08BUYS45
      - MRAM_Everspin_MR4A08BCMA35
      - ReRAM chips are missing and not added in this function.

    Args:
        db_handler (DBHandler): The database handler used to add memory instances.
        logger (logging.Logger): Logger instance for logging operations.

    Note:
        The test_ctr field is used to differentiate between old and new chips:
        - 9999 indicates old chips with unknown test counters.
        - 0 indicates new chips.

    """

    logger.info("Adding memory instances to the database.")

    # Add FRAM_Rohm_MR48V256C
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeLaR1', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FRAM R5', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FRAM R7', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})

    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa1', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa2', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa3', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa4', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa5', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa6', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa7', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa8', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa9', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'FeLa10', 'comment': 'new chip',
         'memory_type_label': 'FRAM_Rohm_MR48V256C'})

    # Add FRAM_Fujitsu_MB85R1001ANC_GE1
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeFJ1', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Fujitsu_MB85R1001ANC_GE1'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeFJ2', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Fujitsu_MB85R1001ANC_GE1'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeFJ3', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Fujitsu_MB85R1001ANC_GE1'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeFJ4', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Fujitsu_MB85R1001ANC_GE1'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeFJ5', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Fujitsu_MB85R1001ANC_GE1'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'FeFJ6', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Fujitsu_MB85R1001ANC_GE1'})

    # Add FRAM_Cypress_FM22L16_55_TG
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'Mem 1', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Cypress_FM22L16_55_TG'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'Mem 3', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Cypress_FM22L16_55_TG'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'Mem 4', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'FRAM_Cypress_FM22L16_55_TG'})

    # Add MRAM_Everspin_MR4A08BUYS45
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'MrE45.1', 'comment': 'new chip',
         'memory_type_label': 'MRAM_Everspin_MR4A08BUYS45'})
    db_handler.add_memory_instance(
        {'test_ctr': 9999, 'label': 'MrE45.R2', 'comment': 'old_chip_unknown test_ctr',
         'memory_type_label': 'MRAM_Everspin_MR4A08BUYS45'})

    # Add MRAM_Everspin_MR4A08BCMA35
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'MrE35.1', 'comment': 'new chip',
         'memory_type_label': 'MRAM_Everspin_MR4A08BCMA35'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'MrE35.2', 'comment': 'new chip',
         'memory_type_label': 'MRAM_Everspin_MR4A08BCMA35'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'MrE35.3', 'comment': 'new chip',
         'memory_type_label': 'MRAM_Everspin_MR4A08BCMA35'})
    db_handler.add_memory_instance(
        {'test_ctr': 0, 'label': 'MrE35.4', 'comment': 'new chip',
         'memory_type_label': 'MRAM_Everspin_MR4A08BCMA35'})

    # All ReRAM chips are missing!
