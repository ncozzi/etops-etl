## Pending features on datasets & code
* Needless to say, no pull request was performed; this should change in practice
* There is **zero unit testing** in the code; this would be absolutely vital in production, and should test: that the pipeline runs, that all calculations are as expected, that Airflow DAGs are correctly configured, etcetera
* No ex-post **data quality** check is done; this would be highly recommended (and should be automated)
* Due to set time constraints, **not all attributes were tested or transformed**; of course this would in practice be different, and would involve a business analyst/data engineer fully dedicated to assessing necessary calculations, transformations, schema and metadata
* **Countries** must be standardized in the future; in practice, the user should not be able to enter a value that is not incorrect - that is, there is only a finite (a la "drop down menu") set of valid entries
* Same with `risk_profile` and pretty much any other attribute that is categorical
* **Exchange rates** were calculated using simple, static conversion rates; in practice, we should have a separate, longitudinal dataset with exchange rates over time
* In practice, all critical information such as `client_name`, `isin`, etcetera, should be tokenized in order to comply with **GDPR laws** - e.g. data engineers should not have access to this information, and only users with authorization shall be able to detokenize

## Pending data architecture changes
* I would personally have each data pipeline into its own separate repository; coding of data pipelines could be standardized into in-house libraries - with elements such as datalake naming, etcetera, also incorporated
* I would also argue that many data transformations could be done with Python instead of `dbt`, and I would add an additional data layer for this purpose - therefore use `dbt` only for the final user access
* Airflow DAGs could be separated into an isolated *Airflow* repository; possibly custom in-house packages could be also created to standardize all coding
* Data is flowing locally in this example. Clear to say, table paths should reference externally - already a shared Onedrive would be a big win; an AWS S3 container or an on-prem storage would be even better
* This current setup uses DBT Core, thus a potential user would not be able to access the SQL server; this would of course need to change in practice
* Tables should be stored with names referencing the respective date of the file - so, for example, instead of `transaction_data.csv` we would have `transaction_data_20250923.csv`
* Speaking of which, `csv` works for now, but for big data `parquet` would be even better