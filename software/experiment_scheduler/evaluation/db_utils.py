import logging
import sqlite3
from typing import List, Optional

from defines import DATABASE_PATH


def query_database(db_path, query: str, params: tuple = ()) -> List:
    """
    Executes an SQL query and returns the results.

    :param db_path: Path to the SQLite database file.
    :param query: SQL query to execute.
    :param params: Tuple of parameters for the SQL query.
    :return: List of query results.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error while performing sqlite query ({query}:{params}): {e}")
        return []
    finally:
        if conn is not None:
            conn.close()


def get_reliability_test_configs(database_path="../memories.db", mem_name: str = 'all') -> List:
    """
    Retrieves reliability test configurations from the specified SQLite database, with an optional filter on memory type name.

    Parameters:
        database_path: Path to the SQLite database file. Default is "memories.db".
        mem_name (Optional[str]): If provided, filters the test configurations by memory type name.

    Returns:
        list of tuples: Each tuple contains (memory_instance_id, config_file, test_parameter_json, test_id).
        If no test configurations are found, returns an empty list.
    """
    if mem_name == 'all':
        sql_query = '''
            SELECT memory_instance_id, config_file, test_parameter_json, test_id
            FROM test_configs
            WHERE test_type = "reliable" 
        '''
        return query_database(database_path, sql_query)
    else:
        sql_query = '''
            SELECT tc.memory_instance_id, tc.config_file, tc.test_parameter_json, tc.test_id
            FROM test_configs as tc, memory_instances as mi, memories as m
            WHERE tc.test_type = "reliable" and tc.memory_instance_id = mi.id and mi.memory_type_id = m.id and m.name = ?
        '''
        return query_database(database_path, sql_query, (mem_name,))


def fetch_memory_instance_details(memory_instance_id: int):
    memory_instance_query = '''
        SELECT label, memory_type_id 
        FROM memory_instances 
        WHERE id = ?
    '''
    ret_val = query_database(DATABASE_PATH, memory_instance_query, (memory_instance_id,))
    if not ret_val:
        logging.warning(f"No memory instance found for ID {memory_instance_id}")
        return None
    return ret_val


def get_all_instances_of_type(memory_identifier: str):
    """
    Fetch all instances of a given memory type from the database.

    Args:
    - memory_identifier (str): The name of the memory type to query for.

    Returns:
    - list: A list of memory instance IDs that correspond to the specified memory type.
    """

    query_res = query_database(
        DATABASE_PATH,
        'SELECT mi.id FROM memory_instances as mi, memories as m WHERE m.name=? and m.id = mi.memory_type_id',
        # SQL query
        params=tuple([memory_identifier])  # Parameters to be used in the query (memory identifier)
    )

    return [x[0] for x in query_res]


def fetch_memory_type_details(memory_type_id: int):
    """
    Fetches memory type details from the database for a given memory type ID.

    Args:
        memory_type_id (int): ID of the memory type to fetch.

    Returns:
        list or None: A list containing one tuple with (name, data_width, max_addr) if found,
                      otherwise None if the memory type does not exist.
    """
    memory_type_query = '''
        SELECT name, data_width, max_addr 
        FROM memories 
        WHERE id = ?
    '''
    memory_type = query_database(DATABASE_PATH, memory_type_query, (memory_type_id,))

    if not memory_type:
        logging.warning(f"No memory type found for ID {memory_type_id}")
        return None
    return memory_type
