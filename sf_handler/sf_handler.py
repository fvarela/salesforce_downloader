from simple_salesforce import Salesforce
import logging
logger = logging.getLogger('main')
import time
from db_handler.db_handler import SQLiteDBHandler


def sf_login(user, password, security_token):
    sf = Salesforce(
        username=user,
        password=password,
        security_token=security_token
    )
    return sf

class SalesforceJob:
    def __init__(self, user, password, security_token, name, query, target_json_path, incremental_field_name, incremental_field_default_value):
        self.name = name
        self.base_query = query
        self.target_json_path = target_json_path
        self.sf = sf_login(user, password, security_token)
        self.incremental_field_name = incremental_field_name
        self.incremental_field_default_value = incremental_field_default_value

    def get_last_incremental_field_value(self):
        with SQLiteDBHandler() as db_handler:
            incremental_field_value = db_handler.get_latest_incremental_value(self.name)
            if incremental_field_value is None:
                logger.info(f"Job: {self.name}. No previous incremental value found. Using default value: {self.incremental_field_default_value}")
                incremental_field_value = self.incremental_field_default_value
        return incremental_field_value 
    def _format_query(self):
        incremental_field_value = self.get_last_incremental_field_value()

        return self.base_query.format(incremental_field_name=self.incremental_field_name, 
                                      incremental_field_value=incremental_field_value)

    def _parse_record(self, record, object_name=None):
        try:
            entry = {}
            for key, value in record.items():
                if key == 'attributes':
                    continue
                elif isinstance(value, dict):
                    nested_entry = self._parse_record(value, object_name=key)
                    for nested_key, nested_value in nested_entry.items():
                        entry_key = f"{key}_{nested_key}" if object_name is None else f"{object_name}_{nested_key}"
                        entry[entry_key] = nested_value
                else:
                    entry_key = f"{object_name}_{key}" if object_name else key
                    entry[entry_key] = value
            return entry
        except Exception as e:
            logger.error(f"Error parsing record: {e}")
            return {}

    def execute(self):
        self.query = self._format_query()
        records = self.sf.query(self.query)
        with SQLiteDBHandler() as db_handler:
            for record in records['records']:
                record = self._parse_record(record)
                db_handler.upsert_entry(table_name=self.name, record=record)
        self.export_to_json(name=self.name, target_json_path=self.target_json_path)
        if len(records['records']) > 0:
            last_incremental_value = records.get('records')[-1][self.incremental_field_name]
            with SQLiteDBHandler() as db_handler:
                db_handler.upsert_entry(self.name, {'Id': 'incremental_field_value', 'incremental_value': last_incremental_value})
        return len(records['records'])
    
    def export_to_json(self, name, target_json_path):
        with SQLiteDBHandler() as db_handler:
            db_handler.export_to_json(name, target_json_path)