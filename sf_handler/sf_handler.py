from simple_salesforce import Salesforce
import logging
logger = logging.getLogger('main')
import time
from db_handler.db_handler import SQLiteDBHandler
from aux_tools.my_style import mystyle


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
        records_parsed = 0
        self.query = self._format_query()
        logger.info(f"\nStarting job {self.name} at {time.strftime('%Y-%m-%d %H:%M:%S')}.\n")
        logger.info(f"Job {self.name} query: {self.query}")
        response = self.sf.query(self.query)
        total_start_time = time.time()

        while True:
            start_time = time.time()
            with SQLiteDBHandler() as db_handler:
                for i, record in enumerate(response['records']):
                    record = self._parse_record(record)
                    db_handler.upsert_entry(table_name=self.name, record=record, incremental_field_name=self.incremental_field_name)
                    if i == len(response['records']) - 1:
                        records_parsed += len(response['records'])
                        elapsed_time = time.time() - start_time
                        last_incremental_value = record.get(self.incremental_field_name, '')
                        print(f"Job {mystyle.bright}{self.name}{mystyle.done} parsed {mystyle.good}{len(response['records'])}{mystyle.done} records in the last loop. Elapsed time: {mystyle.good}{elapsed_time:.2f}{mystyle.done} seconds. Latest {mystyle.bright}{self.incremental_field_name}{mystyle.done}:{mystyle.good}{last_incremental_value}{mystyle.done}")
            if not response['done']:
                response = self.sf.query_more(response['nextRecordsUrl'], True)
            else:
                break
        logger.info(f"Job {self.name} DONE! It parsed a total of {records_parsed} records in {round(time.time() - total_start_time, 2)}seconds.")
        self.export_to_json(name=self.name, target_json_path=self.target_json_path)
        print(f"Job {mystyle.bright}{self.name}{mystyle.done} {mystyle.good}DONE!{mystyle.done}. It parsed a total of {mystyle.good}{records_parsed}{mystyle.done} records in {mystyle.good}{round(time.time() - total_start_time, 2)}{mystyle.done} seconds.")

    
    def export_to_json(self, name, target_json_path):
        with SQLiteDBHandler() as db_handler:
            db_handler.export_to_json(name, target_json_path)