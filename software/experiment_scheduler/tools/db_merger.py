'''
This tool allows merging two measurement databases.
This is necessary, for example, when running two experiments in parallel on two computers.
The resulting databases can afterwards be merged, allowing for the analysis of the merged dataset.

Author: Florian Frank
Affiliation: University of Passau - Chair of Computer Engineering
'''

import sys
import argparse
import sqlite3
import logging


def handle_command_line_arguments() -> dict:
    parser = argparse.ArgumentParser(
        description="Merge two or more SQLite database files."
    )
    parser.add_argument(
        "databases",
        nargs="+",
        help="Input database files (at least two) followed by the output file."
    )

    args = parser.parse_args()

    if len(args.databases) < 3:
        parser.error("You must provide at least two input DB files and one output DB file.")

    return {'input': args.databases[:-1], 'output': args.databases[-1]}


def print_header():
    print("***********************************************")
    print("*****************DB Merge Tool*****************")
    print("***********************************************\n\n")


def open_database(database_name: str):
    logging.info(f"Open Database {database_name}")
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    return con, cur


def close_database(db_obj):
    logging.info(f"Closing Database")
    db_obj.close()


def copy_database_scheme(cursor_input_db, cursor_output_db, output_db_obj):
    """
    This function retrieves the scheme of a database and sets up the same scheme
    on a fresh output database.
    """
    logging.info(f"Retrieve db scheme from first input database")
    cursor_input_db.execute("""
              SELECT type, name, sql
              FROM sqlite_master
              WHERE sql IS NOT NULL
              ORDER BY type='table' DESC, type='index' DESC
          """)
    db_scheme = cursor_input_db.fetchall()

    logging.info(f"Apply db scheme to output database")
    for obj_type, name, sql in db_scheme:
        try:
            cursor_output_db.execute(sql)
        except Exception as e:
            print(f"Failed to create {obj_type} '{name}': {e}")

    output_db_obj.commit()


def copy_all_data(cursor_input_db, input_db_obj, cursor_output_db, output_db_obj):
    '''
    This function copies all the table content from a database to an
    output database as reference.
    '''
    cursor_input_db.execute("""
               SELECT name FROM sqlite_master
               WHERE type='table'
                 AND name NOT LIKE 'sqlite_%';
           """)
    tables = [row[0] for row in cursor_input_db.fetchall()]

    for table in tables:
        logging.info(f"Copying table: {table}")

        cursor_input_db.execute(f"SELECT * FROM {table}")
        rows = cursor_input_db.fetchall()

        if not rows:
            continue  # Skip as there is nothing to insert

        col_names = [desc[0] for desc in cursor_input_db.description]
        col_list = ", ".join(col_names)
        placeholders = ", ".join(["?"] * len(col_names))

        insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

        # Get maximum ID for insertion
        cursor_output_db.execute("SELECT MAX(id) FROM memories")
        max_id = cursor_output_db.fetchone()[0] or 0

        for row in rows:
           row_new = list(row)
           row_new[0] = row_new[0] + max_id + 1
           cursor_output_db.execute(insert_sql, tuple(row_new))

    output_db_obj.commit()
    logging.info("Data completely transferred.")

def _table_query_helper(source_cursor, destination_cursor, table_name):
   source_cursor.execute(f"SELECT * FROM {table_name}")
   rows_src = source_cursor.fetchall()

   destination_cursor.execute(f"SELECT * FROM {table_name}")
   rows_dest = destination_cursor.fetchall()

   return rows_src, rows_dest

def _filter_unique_entries(field_idx, cmp_entries, x):
   for y in cmp_entries:
      if x[field_idx] == y[field_idx]:
         return False
   return True

def _insertion_helper(destination_cursor, filtered_rows, table_name):
   if len(filtered_rows) > 0:
      num_columns = len(filtered_rows[0])
      placeholders = ", ".join(["?"] * num_columns)
      insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

      identifier = 'id'
      if table_name == 'test_configs':
         identifier = 'test_id'

      destination_cursor.execute(f"SELECT MAX({identifier}) FROM {table_name}")
      max_id = destination_cursor.fetchone()[0] or 0

      for i, row in enumerate(filtered_rows):
         max_id += 1
         row_new = [max_id] + list(row[1:])
         destination_cursor.execute(insert_sql, tuple(row_new))

      logging.info(f"Insertion of new {table_name} rows completed.")

def merge_memory_rows(source_cursor, destination_cursor, destination_conn):
   """
   Detects memory types not available in destination database and adds them.
   The memory modules are identified by their name. Furthermore it updates the corresponding memory timing config.
   """
   TABLE_NAME = "memories"
   INDEX_MEM_NAME = 1

   rows_src, rows_dest = _table_query_helper(source_cursor, destination_cursor, TABLE_NAME)
   filtered_rows = list(filter(lambda x: _filter_unique_entries(INDEX_MEM_NAME, rows_dest ,x), rows_src))
   logging.info(f"Detected {len(filtered_rows)} memory modules to merge")
   _insertion_helper(destination_cursor, filtered_rows, TABLE_NAME)
   destination_conn.commit()

   TABLE_NAME_TIMING = "memory_timing_config"


   rows_src, rows_dest = _table_query_helper(source_cursor, destination_cursor, TABLE_NAME_TIMING)
   filtered_rows = list(filter(lambda x: _filter_unique_entries(INDEX_MEM_NAME, rows_dest ,x), rows_src))
   logging.info(f"Detected {len(filtered_rows)} timing value to merge")
   _insertion_helper(destination_cursor, filtered_rows, TABLE_NAME)
   destination_conn.commit()


def merge_memory_instance_table(source_cursor, destination_cursor, destination_conn):
   """
   Currently only adds
   """
   TABLE_NAME = "memory_instances"
   INDEX_MEM_NAME = 0

   # Add memory instances not included in the destination table
   # Currently only works if the ids of memory instances are matching
   rows_src, rows_dest = _table_query_helper(source_cursor, destination_cursor, TABLE_NAME)
   filtered_rows = list(filter(lambda x: _filter_unique_entries(INDEX_MEM_NAME, rows_dest ,x), rows_src))
   logging.info(f"Detected {len(filtered_rows)} new memory instances")
   rows_src, rows_dest = _table_query_helper(source_cursor, destination_cursor, TABLE_NAME)

   # in a next step harmonize the experiment counter (simply add them)
   for row_src in rows_src:
      for row_dest in rows_dest:
         if row_src[0] == row_dest[0]:
            new_ctr_value = row_src[1] + row_dest[1]
            destination_cursor.execute("""
               UPDATE memory_instances
               SET test_ctr = ?
               WHERE id = ?
            """, (new_ctr_value, row_dest[0]))
            logging.info(f"Updated counter value of {row_dest[3]}: {row_dest[1]} -> {new_ctr_value}")
   destination_conn.commit()


def merge_test_configs(source_cursor, destination_cursor, dest_conn):
   TABLE_NAME = "test_configs"
   INDEX_MEM_NAME = 4

   rows_src, rows_dest = _table_query_helper(source_cursor, destination_cursor, TABLE_NAME)
   filtered_rows = list(filter(lambda x: _filter_unique_entries(INDEX_MEM_NAME, rows_dest, x), rows_src))
   logging.info(f"Detected {len(filtered_rows)} memory modules to merge")
   _insertion_helper(destination_cursor, filtered_rows, TABLE_NAME)
   dest_conn.commit()


def update_database_entries(source_cursor, destination_cursor, destination_conn):
   """
   This function updates a database based on the entries of a second database.
   Here, the different memory instances are updated, along with the corresponding timing configurations and the test configurations.
   """
   merge_memory_rows(source_cursor, destination_cursor, destination_conn)
   merge_memory_instance_table(source_cursor, destination_cursor, destination_conn)
   merge_test_configs(source_cursor, destination_cursor, destination_conn)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print_header()
    config_dict = handle_command_line_arguments()

    # Open first input db to copy the db scheme to the output db
    db_obj_input, cursor_input = open_database(config_dict['input'][0])
    db_obj_output, cursor_output = open_database(config_dict['output'])

    # Create all tables within the database
    copy_database_scheme(cursor_input, cursor_output, db_obj_output)

    # Copy content data of first database into output
    copy_all_data(cursor_input, db_obj_input, cursor_output, db_obj_output)

    # Merge ramaining databases
    for db in config_dict['input'][1:]:
      new_db_obj, new_cursor = open_database(db)
      update_database_entries(new_cursor, cursor_output, db_obj_output)
      close_database(new_db_obj)

    close_database(db_obj_input)
    close_database(db_obj_output)
