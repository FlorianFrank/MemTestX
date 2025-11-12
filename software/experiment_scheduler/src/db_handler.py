import json
import os
import sqlite3
import logging

from test_defines import Test, test_type_to_str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBHandler:
    def __init__(self, db_name: str):
        """
        Initialize the database handler with a database name.
        Args:
            db_name (str): Name of the SQLite database file.
        """
        self._db_name = db_name
        self._connection = None
        self._cursor = None
        self._tables = []

    def initialize(self):
        """
        Initialize the database connection and cursor.
        """
        if not os.path.exists(self._db_name):
            logger.info(f"Database '{self._db_name}' does not exist. Creating it.")
        try:
            self._connection = sqlite3.connect(self._db_name)
            self._connection.row_factory = sqlite3.Row
            self._cursor = self._connection.cursor()
            logger.info(f"Connected to database: {self._db_name}")
        except sqlite3.Error as error:
            logger.error(f"Failed to connect to database: {error}")
            raise

    def _create_table_if_not_exists(self, table: str, config: str):
        """
        Creates the specified table in the database if it does not already exist.

        Args:
            table (str): Name of the table to create.
            config (str): Column definitions and constraints for the table.
        """
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                {config}
            );
            """
            self._cursor.execute(query)
            self._connection.commit()  # Commit changes to the database
            self._tables.append(table)
            logger.info(f"`{table}` table created or already exists.")
        except sqlite3.Error as exception:
            logger.error(f"Failed to create the `{table}` table: {exception}")
            raise

    """ ************** 

        Create Tables

    ******************"""

    def create_memory_table(self):
        """
        Creates the `memories` table in the database if it does not already exist.
        """
        config = """
        id INTEGER PRIMARY KEY,
        name TEXT,
        manufacturer TEXT,
        technology TEXT,
        model Text,
        interface_type TEXT,
        data_width INTEGER,
        address_width INTEGER,
        min_addr INTEGER,
        max_addr INTEGER,
        comment TEXT,
        config_file TEXT,
        voltage NUMERIC,
        current NUMERIC
        """
        self._create_table_if_not_exists('memories', config)

    def create_memory_instance_table(self) -> None:
        """
        Creates the `memory_instances` table in the database if it does not already exist.
        """
        config = """
        id INTEGER PRIMARY KEY,
        test_ctr INTEGER,
        memory_type_id INTEGER,
        label TEXT,
        comment TEXT,
        FOREIGN KEY(memory_type_id) REFERENCES memories(id)
        """
        self._create_table_if_not_exists('memory_instances', config)

    def create_timing_parameter_table(self) -> None:
        """
                Creates the `memory_instances` table in the database if it does not already exist.
                """
        config = """
                id INTEGER PRIMARY KEY,
                name TEXT,
                memory_type_id INTEGER,
                ceDrivenWrite BOOLEAN,
                ceDrivenRead BOOLEAN,
                tWaitAfterInit INTEGER,
                tNextRead INTEGER,
                tStartWrite INTEGER,
                tNextWrite INTEGER,
                tACWrite INTEGER,
                tASWrite INTEGER,
                tAHWrite INTEGER,
                tPWDWrite INTEGER,
                tDSWrite INTEGER, 
                tDHWrite INTEGER,
                tStartRead INTEGER,
                tASRead INTEGER,
                tAHRead INTEGER,
                tOEDRead INTEGER,
                tPRCRead INTEGER,
                tCEOEEnableRead INTEGER,
                tCEOEDisableRead INTEGER,
                comment TEXT,
                FOREIGN KEY(memory_type_id) REFERENCES memories(id)
                """
        self._create_table_if_not_exists('memory_timing_config', config)

    def create_test_table(self):
        config = """
                    test_id INTEGER PRIMARY KEY,
                    test_type TEXT,
                    board TEXT,
                    memory_instance_id INTEGER,
                    config_file TEXT,
                    test_parameter_json TEXT,
                    comment TEXT,
                    start TEXT, 
                    end TEXT,
                    FOREIGN KEY(memory_instance_id) REFERENCES memory_instances(id)
                    """
        self._create_table_if_not_exists('test_configs', config)

    """ ************** 
    
     Add data to tables 
    
    ******************"""

    def add_test_entry(self, test: Test):
        try:
            self._cursor.execute("SELECT id FROM memory_instances WHERE label = ?", (test.memory_label,))
            results = self._cursor.fetchall()

            if not results:
                logger.error(f"Could not add test as memory instance with label '{test.memory_label}' was not found!")
                return  # Exit function early

            idn = results[0][0]  # Extract ID correctly

            # Get the max ID from test_configs, handle the case when no entries exist
            self._cursor.execute("SELECT MAX(test_id) FROM test_configs")
            results = self._cursor.fetchone()
            idn_test_inst = results[0] if results[0] is not None else -1

            query = """
                INSERT OR IGNORE INTO test_configs (
                    test_id, test_type, memory_instance_id, board, config_file, test_parameter_json, comment, start, end
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            test.identifier = idn_test_inst + 1

            self._cursor.execute(query, (
                test.identifier,
                test_type_to_str(test.test_template.type),
                idn,
                test.board,
                test.measure_file.get_file_name(),
                json.dumps(test.test_template.parameters),
                test.test_template.comment,
                0, 0
            ))
            self._connection.commit()

            logger.info("Update counter of memory instance")
            query = """
                    UPDATE memory_instances SET test_ctr = test_ctr + 1 WHERE
                    id = ?;
                    """

            self._cursor.execute(query, (idn,))

            self._connection.commit()
            logger.info("Test added successfully.")
            return True

        except sqlite3.Error as error:
            logger.error(f"Failed to add test: {error}")

        return False

    def update_start_ts(self, ts: str, test: Test) -> None:
        logger.info(f"Update start time {ts}")

        query = """
                  UPDATE test_configs SET start = ? WHERE
                  test_id = ?;
                  """

        self._cursor.execute(query, (
            ts,
            test.identifier
        ))
        self._connection.commit()

    def update_stop_ts(self, ts: str, test: Test) -> None:
        logger.info(f"Update start time {ts}")

        query = """
                  UPDATE test_configs SET end = ? WHERE
                  test_id = ?;
                  """
        print(test)
        self._cursor.execute(query, (
            ts,
            test.identifier
        ))
        self._connection.commit()

    def add_memory_type(self, memory_dict: dict):
        """
        Adds a memory type to the `memories` table.

        Args:
            memory_dict (dict): Dictionary containing memory properties such as name, manufacturer, etc.

        Raises:
            sqlite3.Error: If the operation fails.
        """

        self._cursor.execute("SELECT * FROM memories where manufacturer = ? and model = ?",
                             (memory_dict["manufacturer"], memory_dict["model"]))
        results = self._cursor.fetchall()
        if len(results) == 0:
            query = """
            INSERT OR IGNORE INTO memories (
                name, manufacturer, technology, model, interface_type, 
                data_width, address_width, min_addr, max_addr, comment, voltage, current
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            try:
                # Use a parameterized query to avoid SQL injection
                self._cursor.execute(query, (
                    memory_dict.get('name', None),
                    memory_dict.get('manufacturer', None),
                    memory_dict.get('technology', None),
                    memory_dict.get('model', None),
                    memory_dict.get('interface_type', None),
                    memory_dict.get('data_width', None),
                    memory_dict.get('address_width', None),
                    memory_dict.get('min_addr', None),
                    memory_dict.get('max_addr', None),
                    memory_dict.get('comment', "none"),
                    memory_dict.get('voltage', None),
                    memory_dict.get('current', None)
                ))
                self._connection.commit()
                logger.info(f"Memory type '{memory_dict.get('name', 'Unknown')}' added successfully.")
            except sqlite3.Error as error:
                logger.error(f"Failed to add memory: {error}")
                raise
        else:
            logger.warning(f"Ignore duplicate memory entry")

    def add_memory_timing_parameter(self, timing_dict: dict):
        try:
            # Check if memory instance already exists
            self._cursor.execute("SELECT * FROM memory_timing_config where name = ?",
                                 (timing_dict["name"],))
            results = self._cursor.fetchall()
            if len(results) == 0:
                # Check if the memory type exists
                self._cursor.execute("SELECT id FROM memories where name = ?",
                                     (timing_dict["name"],))

                result = self._cursor.fetchone()
                if result is not None:
                    memory_type_id = result[0]  # Extract the id
                    query = """
                        INSERT OR IGNORE INTO memory_timing_config (
                            name, memory_type_id, ceDrivenWrite, ceDrivenRead, tWaitAfterInit, tStartWrite,
                            tNextWrite, tACWrite, tASWrite, tAHWrite, tPWDWrite, tDSWrite, tDHWrite, tStartRead, tNextRead, tASRead,
                            tAHRead, tOEDRead, tPRCRead, tCEOEEnableRead, tCEOEDisableRead, comment
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);
                    """
                    self._cursor.execute(query, (
                        timing_dict.get('name', None),
                        memory_type_id,
                        timing_dict.get('ceDrivenWrite', None),
                        timing_dict.get('ceDrivenRead', None),

                        timing_dict.get('tWaitAfterInit', None),
                        timing_dict.get('tStartWrite', None),
                        timing_dict.get('tNextWrite', None),
                        timing_dict.get('tACWrite', None),

                        timing_dict.get('tASWrite', None),
                        timing_dict.get('tAHWrite', None),
                        timing_dict.get('tPWDWrite', None),
                        timing_dict.get('tDSWrite', None),
                        timing_dict.get('tDHWrite', None),
                        timing_dict.get('tStartRead', None),

                        timing_dict.get('tNextRead', None),
                        timing_dict.get('tASRead', None),
                        timing_dict.get('tAHRead', None),
                        timing_dict.get('tOEDRead', None),
                        timing_dict.get('tPRCRead', None),
                        timing_dict.get('tCEOEEnableRead', None),
                        timing_dict.get('tCEOEDisableRead', None),
                        timing_dict.get('comment', None)
                    ))
                    self._connection.commit()
                    logger.info(f"Timing parameter for memory {timing_dict['name']} added successfully.")
                else:
                    logger.error(f"Timing parameter for memory {timing_dict['name']} not successfully.")
            else:
                logger.warning(f"Timing parameter for memory {timing_dict['name']} already exist.")
        except sqlite3.Error as err:
            logger.error(f"Failed to add timing parameters: {err}")
            raise

    def add_memory_instance(self, memory_dict: dict):
        try:
            # Check if memory instance already exists
            self._cursor.execute("SELECT id FROM memory_instances WHERE label = ?", (memory_dict["label"],))
            if self._cursor.fetchone() is not None:  # If any result exists, log warning and return
                logger.warning(f"Memory with label '{memory_dict['label']}' already exists.")
                return

            # Check if the memory type exists
            self._cursor.execute("SELECT id FROM memories WHERE name = ?", (memory_dict["memory_type_label"],))
            result = self._cursor.fetchone()
            if result is None:
                logger.error(f"Memory type '{memory_dict['memory_type_label']}' not registered.")
                return

            memory_type_id = result[0]  # Extract the memory type ID

            # Insert new memory instance
            query = """
                INSERT INTO memory_instances (
                    test_ctr, memory_type_id, label, comment
                ) VALUES (?, ?, ?, ?);
            """
            self._cursor.execute(query, (
                memory_dict['test_ctr'],
                memory_type_id,
                memory_dict['label'],
                memory_dict.get('comment', None)  # Handle missing 'comment' key
            ))
            self._connection.commit()
            logger.info(f"Memory instance '{memory_dict['label']}' added successfully.")

        except sqlite3.Error as error:
            logger.error(f"Failed to add memory instance: {error}")
            raise  # Decide if this should propagate or just log

    """ **************** 

        Query Data

    ******************"""

    def get_all_tables(self) -> None:
        """
         Retrieve all table names in the database.
         """
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            self._cursor.execute(query)
            results = [row[0] for row in self._cursor.fetchall()]  # Extract table names from query result
            logger.info(f"Retrieved {len(results)} tables from the database: {results}")
            self._tables = results
        except sqlite3.Error as error:
            logger.error(f"Failed to retrieve tables from the database: {error}")
            raise

    def clear_all_tables(self) -> None:
        """
        Clear all tables in the database.
        :return: None
        """
        self.get_all_tables()
        try:
            for table in self._tables:
                query = f"""
                 DROP TABLE IF EXISTS {table}
                 """
                self._cursor.execute(query)
            self._connection.commit()
            logger.info(f"`{self._tables}` dropped.")
            self._tables.clear()
        except sqlite3.Error as error:
            logger.error(f"Failed to drop `{self._tables}` table: {error}")
            raise

    def query_all_memories(self) -> dict:
        """
        Query all records from the `memories` table.
        Returns:
            list: List of rows from the `memories` table.
        """
        try:
            query = "SELECT * FROM memories"
            self._cursor.execute(query)
            results = self._cursor.fetchall()
            logger.info(f"Retrieved {len(results)} records from the `memories` table.")
            return results
        except sqlite3.Error as error:
            logger.error(f"Failed to query the `memories` table: {error}")
            raise

    def get_timing_parameter(self, memory_type_name: str):
        try:
            query = """
            SELECT * FROM memory_timing_config as mc
            JOIN memories as m ON mc.memory_type_id = m.id
            WHERE m.name = ?
            """
            self._cursor.execute(query, (memory_type_name,))
            results = self._cursor.fetchall()
            logger.info(f"Retrieved {len(results)} records from the `memories` table.")
            if len(results) == 1:
                return dict(results[0])
            else:
                logger.error(f"Incorrect number of fetched queries: {len(results)}")
        except sqlite3.Error as error:
            logger.error(f"Failed to query the table: {error}")
            raise

    def get_memory_config(self, memory_type_name: str):
        try:
            query = """
            SELECT * FROM memories WHERE name = ?
            """
            self._cursor.execute(query, (memory_type_name,))
            results = self._cursor.fetchall()
            logger.info(f"Retrieved {len(results)} records from the `memories` table.")
            if len(results) == 1:
                return dict(results[0])
            else:
                logger.error(f"Incorrect number of fetched queries: {len(results)}")
        except sqlite3.Error as error:
            logger.error(f"Failed to query the table: {error}")
            raise

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self._connection:
            self._connection.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    # Create an instance of DBHandler
    db_handler = DBHandler("memories.db")

    try:
        # Initialize the database and create the table
        db_handler.initialize()
        db_handler.clear_all_tables()
        db_handler.create_memory_table()
        db_handler.create_memory_instance_table()

        db_handler.get_all_tables()

        # Query and display all data from the `memories` table
        records = db_handler.query_all_memories()
        for record in records:
            print(record)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        # Ensure the database connection is closed
        db_handler.close()
