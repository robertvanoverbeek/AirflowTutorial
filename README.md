# Hands-on Airflow Tutorial using Google Cloud Composer

#### 3.1. Introduction

voordelen behandelen versus cron jobs:
error handling, including upstream errors (dependencies)
backfilling historical data
monitoring / logging
standard operators enabling connections to many other infrastructures


what is asyclical graph

operators and sensors. 


This script demonstrates the usage of Airflow in an ETL process. In this case we periodically Extract data from some place 
(public BigQuery dataset stackoverflow.posts_questions) over a certain time period and store it in a certain form (Transform) as csv file (Load). 
From there it can be made available as data source for i.g. reporting, for instance for the creation of a (Data Studio) dashboard. As a side note
to this: If you use Power BI in combination with GCP (Google Cloud Platform) it is better to store and leave the data in BigQuery (which is a step in the 
applied DAG below), as this makes securely accessing the data from Power BI easier with the standard BigQuery connector in Power BI.
We believe using a csv file stored in GCP for usage in a Power BI is only advisable if you can make the data publicly available, which is
explained in https://cloud.google.com/storage/docs/access-control/making-data-public

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/DSpyramid.PNG" width="300" height="200">
<sup>source: sensecorp.com</sup>
<br/>
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

Airflow Variables are stored in Metadata Database, so any call to variables would mean a connection to Metadata DB.
Your DAG files are parsed every X seconds. If you use a large number of variable in your DAG could mean you might end
up saturating the number of allowed connections to your database.
To avoid this situation, it is advisable to use a single Airflow variable with JSON value.
For instance this case, under Admin > variables in the UI we will save a key 'dag_xyz_config', with
a a set (replace the values with your project ID and bucket name without the gs:// prefix, as we fill it in below):
{"gcp_project": "ml-test-240115", "gcs_bucket": "airflowbucket_tst"}


context managers and then


step 5/5 Define DAG dependencies / defining the order of the tasks

```
docker run hello-world 
```
to verify that Docker can pull and run images.



