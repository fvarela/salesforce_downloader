### Salesforce Data Exporter Configuration Guide

#### Overview

This guide outlines the steps to configure the Salesforce Data Exporter, a Python script designed to extract specific data sets from Salesforce using SOQL queries for analysis in tools like Power BI. It emphasizes selective data extraction, local storage, flexible analysis, and incremental updates to streamline the data analysis process.

#### Configuration Steps

**1. Generate a Salesforce Security Token**

To ensure secure access to Salesforce, generate a security token from your Salesforce account settings. This token, along with your username, will be required in the config.yaml file. Note: Your password is not stored in the configuration file; you'll be prompted to enter it upon each script execution.

**2. Enter Credentials in config.yaml**

Open the **config.yaml** file and input your Salesforce username and the previously generated security token under the sf section:

```
sf:
    user: "your_username@your_company.com"
    token: "YourSalesforceSecurityToken"
```

**3. Prepare SOQL Queries**

If you're new to SOQL or need to explore your Salesforce data structure, use resources like Salesforce Workbench. This will help you craft accurate SOQL queries to retrieve the precise data you need.

**4. Configure SOQL Queries in config.yaml**

Under the salesforce_jobs section of the **config.yaml** file, enter your SOQL queries. Each query must include an incremental field, such as **LastModifiedDate**, to ensure that only new or updated records are fetched in subsequent script runs. This mechanism ensures your local data remains synchronized with Salesforce.

- **Example Configuration for a Single Job**

The following is an example configuration in config.yaml for extracting account data from Salesforce where the country is USA, and the data is filtered by LastModifiedDate.

```
sf:
    user: "francisco.varela@my_company.com"
    token: "VsadfolksdgfSDGasdgigsdfg"

salesforce_jobs:
    company_accounts:
        query: |
            SELECT
                Id,
                Name,
                Region,
                {incremental_field_name}
            FROM Account
            WHERE Country='USA'
            AND {incremental_field_name} >= {incremental_field_value}
            ORDER BY {incremental_field_name} ASC
        incremental_field:
            field_name: "LastModifiedDate"
            default_value: "2019-01-01T00:00:00.000+0000"
        target_json:
            folder: "salesforce_data/"
            file: "company_accounts.json"
```

This configuration specifies:

The query to run, fetching Id, Name, and Region for accounts in the USA, sorted by the incremental field.
The incremental_field details, including the field name: **LastModifiedDate** and a default value **"2019-01-01T00:00:00.000+0000"** to start data retrieval.
The target_json output location, specifying both the folder and the file name where the extracted data will be saved: **salesforce_data/usa_accounts.json**

Final Steps

After configuring the config.yaml file with your specific queries and details, run the script. It will prompt you for your Salesforce password and proceed to execute the defined SOQL queries, saving the fetched data into the specified JSON files for subsequent analysis.
