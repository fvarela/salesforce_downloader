import os
from aux_tools.aux_tools import  create_nested_folders_if_not_exists
import logging
logger = logging.getLogger('main')
import json
import sqlite3



class SQLiteDBHandler:
    def __init__(self):
        self.db_path = os.path.join('my_db', 'sqlite.db')
        create_nested_folders_if_not_exists(self.db_path)
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row 
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_table(self, table_name):
        create_table_sql = f'''CREATE TABLE IF NOT EXISTS {table_name} (
                                key TEXT PRIMARY KEY,
                                value JSON,
                                incremental_value TEXT
                               )'''
        cursor = self.conn.cursor()
        cursor.execute(create_table_sql)
        self.conn.commit()

    def upsert_entry(self, table_name, record):
        self.create_table(table_name)  # Ensure table exists
        # Extract incremental_value from the record's JSON data
        incremental_value = record.get('incremental_value', '')
        upsert_sql = f'''INSERT INTO {table_name} (key, value, incremental_value)
                         VALUES (?, ?, ?)
                         ON CONFLICT(key) DO UPDATE SET
                         value = excluded.value,
                         incremental_value = excluded.incremental_value;'''
        cursor = self.conn.cursor()
        cursor.execute(upsert_sql, (record['Id'], json.dumps(record), incremental_value))
        self.conn.commit()

    def get_latest_incremental_value(self, table_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT MAX(incremental_value) FROM {table_name}")
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.OperationalError as e:
            return None


    def get_available_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]

    def delete_table(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"DROP TABLE {table_name}")
        self.conn.commit()

    def export_to_json(self, table_name, target_json_path):
        select_all_sql = f'''SELECT value FROM {table_name}'''
        cursor = self.conn.cursor()
        cursor.execute(select_all_sql)
        records = cursor.fetchall()
        records_dict_list = [json.loads(dict(record).get('value')) for record in records]
        os.makedirs(os.path.dirname(target_json_path), exist_ok=True)
        with open(target_json_path, 'w') as f:
            json.dump(records_dict_list, f)

        