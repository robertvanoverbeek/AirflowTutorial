"""
This script demonstrates the usage of Airflow in an ETL process. In this case we periodically Extract data from some place
(public BigQuery dataset stackoverflow.posts_questions) over a certain time period and store it in a certain form (Transform) as csv file (Load).
From there it can be made available as data source for e.g. reporting or ML.

Generally the structure of an Airflow DAG consists of 5 parts:
1. importing the modules and declaring variables
2. default arguments
3. instantiation of the DAG
4. the tasks
5. dependencies / order

In the code below we will reference to these steps.

For this DAG you need to save key-value pairs in Airflow (via Admin > Variables) for the following items:
* gcp_project - Your Google Cloud Project ID.
* gcs_bucket - The Google Cloud Storage bucket to save the output file to. This also implies you have created such a bucket.
In the code below, at step 1, we will explain how to implement the variables.
Check https://airflow.apache.org/concepts.html#variables if you want more information about Airflow variables.
Check https://cloud.google.com/storage/docs/creating-buckets if you need more information on creating a gcp bucket,
as this is beyond the scope of this Airflow POC example.

The used DAG is inspired by https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/composer/workflows/bq_notify.py
In the above-mentioned github repo you can also find more examples.
"""

# step 1/5, importing modules and declaring variables
from datetime import date, datetime, timedelta
# from airflow import macros
from airflow import DAG
from airflow import models
from airflow.contrib.operators import bigquery_operator
from airflow.contrib.operators import bigquery_to_gcs
from airflow.operators import bash_operator
from airflow.utils import trigger_rule

"""
Variables taken from Airflow variables as described above.
For some static variables, like references to project names and storage locations,
it can be useful to separate them from the code itself. This is also very useful if you
apply the variables to multiple DAG files. Then, if you then need to change the variable you only
have to change it in a single location.
Airflow Variables are stored in Metadata Database, so any call to variables would mean a connection to Metadata DB.
Your DAG files are parsed every X seconds. If you use a large number of variable in your DAG could mean you might end
up saturating the number of allowed connections to your database.
To avoid this situation, it is advisable to use a single Airflow variable with JSON value.
For instance this case, under Admin > variables in the UI we will save a key 'dag_xyz_config', with
a a set (replace the values with your project ID and bucket name without the gs:// prefix, as we fill it in below):
{"gcp_project": "ml-test-240115", "gcs_bucket": "airflowbucket_tst"}
"""
dag_vars = models.Variable.get("dag_xyz_config", deserialize_json=True)
gcp_project_name = dag_vars["gcp_project"]
gcs_bucket_name = dag_vars["gcs_bucket"]

# other variables:
bq_dataset_name = 'airflow_bq_dataset_{{ ds_nodash }}'
bq_recent_questions_table = bq_dataset_name + '.recent_questions'
bq_most_popular_table_name = 'most_popular'
bq_most_popular_table_id = bq_dataset_name + '.' + bq_most_popular_table_name
output_file = 'gs://{gcs_bucket}/recent_questions_{datestamp}.csv'.format(gcs_bucket=gcs_bucket_name, datestamp = '{{ ds_nodash }}')


# define the best start and end dates:
# we look minimum 3 months back because the public dataset is not updated very frequently
firstday_five_months_back = ((((((date.today().replace(day=1) + timedelta(days=-1)).replace(day=1) +
                         timedelta(days=-1)).replace(day=1) + timedelta(days=-1)).replace(day=1)) +
                            timedelta(days=-1)).replace(day=1) + timedelta(days=-1)).replace(day=1)
firstday_three_months_back = ((((date.today().replace(day=1) + timedelta(days=-1)).replace(day=1) +
                         timedelta(days=-1)).replace(day=1) + timedelta(days=-1)).replace(day=1))
"""
Setting the query window:
in this case we take a short time window of only one week.
We use Airflow macros, using Jinja template to look 7 days back from the run dates.
{{ macros.ds_add(ds, -7) }} corresponds to a date 7 days before the DAG was run.
More info: https://airflow.apache.org/macros.html and / or https://diogoalexandrefranco.github.io/about-airflow-date-macros-ds-and-execution-date/
"""
max_query_date = '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d") }}'
min_query_date = '{{ (execution_date - macros.timedelta(days=7)).strftime("%Y-%m-%d") }}'

# step 2/5, default arguments, which are passed on to all tasks via the instatiated dag in the following step:
default_dag_args = {
     # note the addition of time to the date, without which it will return an error.
     # you can also use the datetime function, for instance: datetime(2019, 1, 1)
    'start_date': datetime.combine(firstday_five_months_back, datetime.min.time()),
    'end_date': datetime.combine(firstday_three_months_back, datetime.min.time()),
     # in case you want backfill (called catchup), determined in step 3, I noticed it is best to select True for depends on the past.
     # this will make jobs running in sequence instead of simultaneously, creating risks for errors with low cpu in this test case.
    'depends_on_past': True,
    'email': 'bla@bla.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
    'project_id': gcp_project_name
    # Note, in this DAG project_id is only used in one task (t2), so instead of declaring it here, we could have added the following
    # parameter line at task 2: project_id = gcp_project_name.
}

"""
step 3/5, instantiation of the DAG and step 4/5, the tasks of the DAG, combined:
In order to limit code repetition, it is good practice to use a DAG
as context managers and then assign new operators to that DAG as shown below.
check https://airflow.apache.org/concepts.html for more information.
"""
with DAG(
     # name of the DAG:
    'popular_stackoverflow_questions_v1',
    default_args=default_dag_args,

    # scheduler interval. You can use cron notation or use
    # preset intervals (https://airflow.apache.org/scheduler.html)
    schedule_interval='@monthly',
    catchup=True
    ) as dag:

    # Create BigQuery output dataset.
    t1_make_bq_dataset = bash_operator.BashOperator(
        task_id='make_bq_dataset',
        bash_command='bq ls {} || bq mk {}'.format(bq_dataset_name, bq_dataset_name))


    # Query recent StackOverflow questions.
    t2_bq_recent_questions_query = bigquery_operator.BigQueryOperator(
        task_id='bq_recent_questions_query',
        bql="""
        SELECT title, view_count
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        WHERE creation_date <= CAST('{max_date}' AS TIMESTAMP)
            AND creation_date >= CAST('{min_date}' AS TIMESTAMP)
        ORDER BY view_count DESC
        LIMIT 50
        """.format(max_date=max_query_date, min_date=min_query_date),
        use_legacy_sql=False,
        destination_dataset_table=bq_recent_questions_table)

    # Export query result to Cloud Storage.
    t3_export_questions_to_gcs = bigquery_to_gcs.BigQueryToCloudStorageOperator(
        task_id='export_recent_questions_to_gcs',
        source_project_dataset_table=bq_recent_questions_table,
        # note: in https://github.com/apache/airflow/blob/master/airflow/contrib/operators/bigquery_to_gcs.py you can see that
        # the type of 'destination_cloud_storage_uris' is list.
        destination_cloud_storage_uris=[output_file],
        export_format='CSV')

    # Delete the bq dataset
    t4_delete_bq_dataset = bash_operator.BashOperator(
        task_id='delete_bq_dataset',
        bash_command='bq rm -r -f %s' % bq_dataset_name,
        # ALL_SUCCESS must be capital
        trigger_rule=trigger_rule.TriggerRule.ALL_SUCCESS)

    # step 5/5 Define DAG dependencies / defining the order of the tasks
    t1_make_bq_dataset >> t2_bq_recent_questions_query >> t3_export_questions_to_gcs  >> t4_delete_bq_dataset
