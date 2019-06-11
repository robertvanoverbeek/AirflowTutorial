# Hands-on Airflow Tutorial using Google Cloud Composer

### 1. Introduction
The aim of this Airflow tutorial is to explain the main principles of Airflow and to provide you with a hands-on working example to get you up to speed with Airflow. Following the definition of Airflow, 'Airflow is a platform to programmatically author, schedule and monitor workflows. Airflow is not a data streaming solution.

I wrote this tutorial as a Data Scientist and I believe many people would say Airflow is a tool for Data Engineers to implement ETL processes. Though, for several reasons I believe that being able to perform some Data Engineering tasks as a Data Scientist is a valuable asset:

* With the rise of Cloud providers like AWS, GCP and Azure, which offer a suite of offerings (storage, streaming, Apps, Web, ML), the traditional Data Science pyramid as shown below becomes increasingly vertically integrated. These movements make it easier and faster to create end-to-end solutions in the cloud, even for a small team or as a single person (e.g. https://aws.amazon.com/blogs/machine-learning/build-end-to-end-machine-learning-workflows-with-amazon-sagemaker-and-apache-airflow/). Artificial intelligence, Internet of things and analytics are the upsell technologies for cloud vendors;
* Quite often companies do not have dedicated DS an DE teams, as most companies do not handle terabytes of data daily and/or streaming data (Big data). Even if they have both, either of the two might not be available at that time due to other priorities. This makes it an asset to be able to do work on both. Besides, if you, as a Data Scientist or an Engineer, can prototype a working Proof-Of-Concept (most likely involving both DE and DS work), it then becomes easier to convince others within the company about the value that can be created.

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/DSpyramid.PNG" width="300" height="200">
<sup>source: sensecorp.com</sup>
<br/>

### 2. Advantages of working with Airflow
Working with Airflow provides you with a number of advantages as opposed to working with e.g. traditional cron jobs:
* It has good facilities with respect to error handling, including upstream errors (dependencies);
* It facilitates backfilling of historical data;
* Built in Monitoring / logging;
* Based on widely used Python;
* There is a large user group contributing by building standard operators, enabling connections to many other infrastructures. These can be found in 'contrib' on https://github.com/apache/airflow/tree/master/airflow/contrib;
* Integration in the cloud with big data and machine learning. You can build end-to-end (ML) solutions in the cloud with Airflow in combination with the other cloud services;
* Thanks to the ease of use data engineers and data scientists don't waste much time on DevOps.

### 3. Setting up the Airflow environment in Google Cloud Platform (GCP)
We will set up an Airflow environment in Google Cloud. Google has integrated Airflow in its offering Cloud Composer, with which setting up and Airfow environment is just a few clicks away. In addition GCP comes with a free $300,- trial credit per google account (gmail account) for a one year period.

Within your Google Account launch your Google cloud console (https://console.cloud.google.com) and navigate to 'Composer' via the 'hamburger' icon in the top left corner. You will then see the options as displayed in the following visual:

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerMenu.PNG" width="774" height="265">
<br/>
One note beforehand: in this screen you see a delete button with which you can delete the environment after usage in order to avoid unnecessary costs!

To create an environment:
* You may tick the box beta features to be able to use the latest functionalities;
* Select 'CREATE'

In the screen that follows, it is very easy to set up a basic Airflow Environment. Fill in:
* A name for the environment;
* Select a location closest to you. For instance europe-west1-d. Check https://cloud.google.com/compute/docs/regions-zones/ if you want to know more about server locations;
* Machine type. For this tutorial you may choose the smallest configuration in terms of CPUs;
* Disk size. At the time of writing the minimum is 20GB;
* Python version. Select Python version 3.
* Lastly click 'CREATE'.

After a few minutes you will notice that the creation of the environment has been completed. You will then be able to drill down on it, where you will find the following screen (the option 'node configuration' will become visible if you click 'EDIT'):

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerConfig.png" width="820" height="767">
<br/>

The environment comes pre-installed with a number of Python packages, such as:

Pandas, google-cloud-bigquery, google-cloud-dataflow, google-cloud-storage, Pandas-gbq, tensorflow and kubernetes.

When you use the button 'PYPI PACKAGES' you will be able to select more Python packages (more information on: https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies).

In order to deploy a DAG file, drill down on the link DAGs folder. In chapter 5 I will explain how you can deploy the DAG of this repository (contained in the DAG folder of this repository), but before that I will explain the structure of this DAG and how to build one in chapter 4.

### 4. DAG structure and building a DAG
With Airflow you can deploy DAGs, which stands for Directed Acyclic graph. This is a finite directed graph with no directed cycles. So it always goes in one direction and does not form a circle. The simple DAG for this tutorial is shown below: 
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowgraphview.PNG" width="955" height="75">
<br/>
This DAG script of this tutorial demonstrates the usage of Airflow in an ETL process. In this case it periodically Extracts data from some place (public BigQuery dataset stackoverflow.posts_questions) over a certain time period and store it in a certain form (Transform) as csv file (Load). From there it can be made available as data source for e.g. reporting (e.g. very simple with Google's Data Studio) and/or Machine Learning. Side note: If you want to use Power BI in combination with GCP it is better to store and leave the data in BigQuery (which is also a step in the DAG of this tutorial), as this makes securely accessing the data from Power BI easier with the standard BigQuery connector in Power BI. I believe using a csv file stored in GCP for usage in a Power BI is only advisable if you can make the data publicly available, which step is explained in https://cloud.google.com/storage/docs/access-control/making-data-public.

While our DAG is quite simple in terms of processes it possesses some extra features that also highlight some functionalities of Airflow:
* Centrally stored variables;
* The usage of Macros and Jinja Templating;
* Backfilling of historical data;
* Use a DAG as context managers.

Generally, the structure of an Airflow DAG consists of 5 parts:
1. Importing the modules and declaring variables, including referencing the centrally stored variables;
2. Default arguments;
3. Instantiation of the DAG;
4. The tasks;
5. Dependencies / order of the flow.

I will explain these five steps using our DAG as an example.

#### 4.1 Modules and variables
The main code elements of part 1 of the DAG file are:
```
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow import models
from airflow.contrib.operators import bigquery_operator
from airflow.contrib.operators import bigquery_to_gcs
from airflow.operators import bash_operator
from airflow.utils import trigger_rule

dag_vars = models.Variable.get("dag_xyz_config", deserialize_json=True)
gcp_project_name = dag_vars["gcp_project"]
gcs_bucket_name = dag_vars["gcs_bucket"]

max_query_date = '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d") }}'
min_query_date = '{{ (execution_date - macros.timedelta(days=7)).strftime("%Y-%m-%d") }}'
```
First of all, the script imports some basic Python datetime functions, which are useful for scheduling the DAG and querying data with date and time stamps.
We import DAG (object), which we will need to instantiate a DAG.
We import 'models' to be able to import the centrally stored variables, which I will explain below.
We then import two operators from 'contrib'. I already briefly mentioned contrib with a link in chapter 2, but under 'contrib' in the Github repository of Airflow you can find standard connectors. The names we use here almost speak for themselves: 'bigquery_operator' to execute queries on BigQuery and 'bigquery_to_gcs' to store BigQuery data in Google Cloud Storage. 
We also import 'bash_operator' to be able to execute bash commands. Airflow provides operators for many common tasks, including ():

* BashOperator - executes a bash command
* PythonOperator - calls an arbitrary Python function
* EmailOperator - sends an email
* SimpleHttpOperator - sends an HTTP request
* MySqlOperator, SqliteOperator, PostgresOperator, MsSqlOperator, OracleOperator, JdbcOperator, etc. - executes a SQL command
* Sensor - waits for a certain time, file, database row, S3 key, etc…

In addition to these basic building blocks, there are many more specific operators: DockerOperator, HiveOperator, S3FileTransformOperator, PrestoToMySqlTransfer, SlackAPIOperator… (check for 'Operators' on https://airflow.apache.org/concepts.html?highlight=connection for more info).

We also import 'trigger_rule'. All operators have a trigger_rule argument which defines the rule by which the generated task get triggered. The default value for trigger_rule is all_success and can be defined as “trigger this task when all directly upstream tasks have succeeded”:

* all_success: (default) all parents have succeeded. We will use this in one of our tasks;
* all_failed: all parents are in a failed or upstream_failed state;
* all_done: all parents are done with their execution;
* etc. etc. Look for 'Trigger Rules' on https://airflow.apache.org/concepts.html

For some static variables, like references to project names and storage locations, it can be useful to separate them from the code itself. This is also very useful if you apply the variables to multiple DAG files. Then, if you then need to change the variable you only have to change it in a single location. With the code: 
```
dag_vars = models.Variable.get("dag_xyz_config", deserialize_json=True)
```
we define the variable 'dag_vars' and retrieve a set of centrally stored variables (JSON, in this case under the name 'dag_xyz_config') with a single command. This is better than retrieving every variable separately. Airflow Variables are stored in Metadata Database, so any call to variables means a connection to Metadata DB. Your DAG files are parsed every X seconds. If you use a large number of variable in your DAG could mean you might end up saturating the number of allowed connections to your database.

In this case, in the UI, under 'Admin' > 'variables' we have to save a key 'dag_xyz_config', with
a a set (replace the values with your Your Google Cloud Project ID and a bucket name without the gs:// prefix):
```
{"gcp_project": "ml-test-xyz", "gcs_bucket": "airflowbucket_tst"}
```
As shown in the screen dump below:
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowvars.png" width="1084" height="214">
<br/>
Check https://cloud.google.com/storage/docs/creating-buckets if you need more information on creating a gcp bucket,
as this is beyond the scope of this Airflow POC example.

Apache Airflow allows the usage of Jinja templating, which makes available multiple helpful variables and macros to aid in date manipulation (https://airflow.apache.org/macros.html and https://diogoalexandrefranco.github.io/about-airflow-date-macros-ds-and-execution-date/). 

In our script we will use the following example of a Jinja template and macro:
```
max_query_date = '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d") }}'
```
This creates a date string in format 'yyy-mm-dd', with the date one day prior to the execution date. I highlight that the execution date can be in the past when applying backfill, which we will use in our script. Later on you will be able to the effects of this in the created log files.

#### 4.2 Default arguments
By defining default arguments, we have the choice to explicitly pass a set of arguments to each task. 

We doen hier wel project_id, maar niet bucket name. Dit had ook gekund. Eventueel testen.

```
default_dag_args = {
    'start_date': datetime.combine(firstday_five_months_back, datetime.min.time()),
    'end_date': datetime.combinefirstday_three_months_back, datetime.min.time()),
    'depends_on_past': True,
    'email': 'bla@bla.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
    'project_id': gcp_project_name
}
```
#### 4.3 Instantiation of the DAG
lfdsaj
```
with DAG(
    'popular_stackoverflow_questions_version_1',
    default_args=default_dag_args,
    schedule_interval='@monthly',
    catchup=True
    ) as dag:
```
#### 4.4 The tasks
lfdsaj
```
t1_make_bq_dataset = bash_operator.BashOperator(
        task_id='make_bq_dataset',
        bash_command='bq ls {} || bq mk {}'.format(bq_dataset_name, bq_dataset_name))
```
#### 4.5 Dependencies / order of the flow
lala
```
t1_make_bq_dataset >> t2_bq_recent_questions_query >> t3_export_questions_to_gcs  >> t4_delete_bq_dataset
```
### 5. Deploying a DAG and checking the logs

Upload the .py file which contains the DAG script.

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowtreeview.PNG" width="1183" height="647">





