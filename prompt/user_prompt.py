import questionary
from aux_tools.my_style import mystyle
from config.config import Config
from sf_handler.sf_handler import SalesforceJob, sf_login
import os
import logging
from db_handler.db_handler import SQLiteDBHandler
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)
import time
class UserPrompt():
    def __init__(self):
        print(f"{mystyle.bright}Welcome to the Salesforce CLI.{mystyle.done}")
        self.config = Config()
        self.config.initialize()
        self.salesforce_jobs = self.config.data.get('salesforce_jobs', [])
        self.username = self.config.get('sf.user')
        self.security_token = self.config.get('sf.token')  
        self.password = None
        self.password = self.prompt_for_salesforce_password()
        self.available_jobs = self.get_available_jobs()

    def prompt_for_salesforce_password(self):
        print(f"Hello {mystyle.bright}{self.username}{mystyle.done}. Please enter your Salesforce password:")
        password = questionary.password("").ask()
        try:
            sf_login(self.username, password, self.security_token)
        except Exception as e:
            print("Press any key to exit.")
            input()
            exit(1)
        print(f"Successfully tested Salesforce logging credentials for {mystyle.bright}{self.username}{mystyle.done}.")
        time.sleep(1)
        return password

    def get_available_jobs(self):
        available_jobs = []
        for job_name, _ in self.salesforce_jobs.items():
            available_jobs.append(job_name)
        return available_jobs

    def main_menu(self):
        while True:
            choice = questionary.select("Please select one of the following options:", choices=["Execute Salesforce Jobs", "Delete local database table", "Exit"]).ask()
            if choice == "Execute Salesforce Jobs":
                questionary.print("Please select a job to run:")
                job_choices = []
                for job_name, _ in self.salesforce_jobs.items():
                    job_choices.append(job_name)
                if len(job_choices) == 0:
                    print(f"{mystyle.bad}No jobs available.{mystyle.done} Returning to main menu.")
                    continue
                job_choices.append("All of them")
                job_choices.append("Cancel and return to main menu")
                selected_job = questionary.select("Job", choices=job_choices).ask()
                if selected_job == "All of them":
                    for job_name, _ in self.salesforce_jobs.items():
                        self.run_job(job_name)
                elif selected_job == "Cancel and return to main menu":
                    continue
                else:
                    self.run_job(selected_job)
            elif choice == "Delete local database table":
                available_tables = []
                with SQLiteDBHandler() as db_handler:
                    available_tables = db_handler.get_available_tables()
                available_tables.append("All tables")
                selected_table = questionary.select("Table", choices=available_tables).ask()
                if selected_table == "All tables":
                    with SQLiteDBHandler() as db_handler:
                        for table in available_tables:
                            if table != "All tables":
                                db_handler.delete_table(table)
                else:
                    with SQLiteDBHandler() as db_handler:
                        db_handler.delete_table(selected_table)

            elif choice == "Exit":
                questionary.print("Exiting.")
                exit(0)

    def run_job(self, job_name):
        job_params = self.salesforce_jobs.get(job_name)
        job_query = job_params.get('query')
        target_json_path = os.path.join(job_params.get('target_json').get('folder'), job_params.get('target_json').get('file'))
        incremental_field_name = job_params.get('incremental_field').get('field_name')
        incremental_field_default_value = job_params.get('incremental_field').get('default_value')  
        sf_job = SalesforceJob(
            user=self.username, 
            password=self.password, 
            security_token=self.security_token, 
            name=job_name, 
            query=job_query, 
            target_json_path=target_json_path,
            incremental_field_name=incremental_field_name,
            incremental_field_default_value=incremental_field_default_value)
        print(f"Starting job {mystyle.bright}{job_name}{mystyle.done} at {time.strftime('%Y-%m-%d %H:%M:%S')}.")
        job_timer = time.time()
        while True:
            loop_timer = time.time()
            entries_parsed = sf_job.execute()
            print(f"Job {mystyle.bright}{job_name}{mystyle.done} parsed {mystyle.good}{entries_parsed}{mystyle.done} records in the last loop. Elapsed time: {mystyle.good}{round(time.time() - loop_timer, 2)}{mystyle.done} seconds. Latests {mystyle.bright}{incremental_field_name}{mystyle.done}:{mystyle.good}{sf_job.get_last_incremental_field_value()}{mystyle.done}")
            # print(f"\tLatests {mystyle.bright}{incremental_field_name}{mystyle.done}:{mystyle.good}{sf_job.get_last_incremental_field_value()}{mystyle.done}")
            if entries_parsed < 10:
                print(f"Job {mystyle.bright}{job_name}{mystyle.done}. Less than {mystyle.good}10{mystyle.done} records were parsed in the last loop. Exiting job.")
                break
        print(f"Job {mystyle.bright}{job_name}{mystyle.done} took {mystyle.good}{round(time.time() - job_timer, 2)}{mystyle.done} seconds to complete.")
