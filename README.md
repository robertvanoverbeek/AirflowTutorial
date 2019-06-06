# Hands-on Airflow Tutorial using Google Cloud Composer

#### 1. Introduction
This tutorial is an introduction to 

voordelen behandelen versus cron jobs:
error handling, including upstream errors (dependencies)
backfilling historical data
monitoring / logging
standard operators enabling connections to many other infrastructures

with airflow in the cloud data engineers and data scientists don't waste much time on DevOps.

integration in the cloud with big data, machine learning. 

you can build end-to-end (ML) solutions in the cloud with Airflow in combination with the other cloud services. 


what is asyclical graph. a pipeline.  Pipelines are designed as a directed acyclic graph by dividing a pipeline into tasks that can be executed independently. Then these tasks are combined logically as a graph.

operators and sensors. 

Databricks has contributed an Airflow operator which enables submitting runs to the Databricks platform.
Airflow has extensive support for the Google Cloud Platform. But note that most Hooks and Operators are in the contrib section.
Airflow has extensive support for Amazon Web Services. But note that the Hooks, Sensors and Operators are in the contrib section.
Airflow has limited support for Microsoft Azure: interfaces exist only for Azure Blob Storage and Azure Data Lake. Hook, Sensor and Operator for Blob Storage and Azure Data Lake Hook are in contrib section.

https://github.com/apache/airflow/tree/master/airflow/contrib

#### 2. Setting up the Airflow environment in GCP
A prerequisite to this is that you have a google account (gmail account), with which you can launch Google Cloud Platform (GCP). GCP comes with $300,- free trial credit.

in GCP navigate to 'Composer' via the 'hamburger' icon in the top left corner. 
selecteer:
click enable beta features and then select create.
note: in this screen you also see a delete button with which you can delete the environment after usage in order to avoid unnecessary costs. 
name, location, machine type (kies het meest eenvoudige), disk size (kies kleinste), python version 3.



then wait a few minutes, after which you can drill down with the link. 

pre installed packages, among others 

	google-cloud-bigquery, google-cloud-dataflow, google-cloud-storage, pandas, pandas-gbq, tensorflow, kubernetes.

Following the link DAGs folder you can upload your DAG file with .py extension. In this case the file in the DAG folder of this repository. 

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

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowgraphview.PNG" width="955" height="75">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowvars.png" width="1084" height="214">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerConfig.png" width="820" height="767">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerMenu.PNG" width="774" height="265">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowtreeview.PNG" width="1183" height="647">

	
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



