# Hands-on Airflow Tutorial using Google Cloud Composer

#### 1. Introduction
The aim of this Airflow tutorial is to explain the main principles of Airflow and to provide you with a hands-on working example to get you up to speed with Airflow as quickly as possible. Following the definition of Airflow, 'Airflow is a platform to programmatically author, schedule and monitor workflows. Airflow is not a data streaming solution. Tasks do not move data from one to the other (though tasks can exchange metadata!). Airflow is not in the Spark Streaming or Storm space, it is more comparable to Oozie or Azkaban'.

I wrote this tutorial as a Data Scientist and I believe many people would say Airflow is a tool for Data Engineers to implement ETL processes. Though, for a number of reasons I believe that being able to perform some Data Engineering tasks as a Data Scientist is a valuable asset:

* With the rise of Cloud providers like AWS, GCP and Azure, which offer a suite of offerings (storage, streaming, Apps, Web, ML), the traditional Data Science pyramid as shown below becomes increasingly vertically integrated. Artificial intelligence, Internet of things and analytics are the upsell technologies for cloud vendors. These movements make it easier and faster to create end-to-end solutions in the cloud, even for a small team or as a single person (e.g. https://aws.amazon.com/blogs/machine-learning/build-end-to-end-machine-learning-workflows-with-amazon-sagemaker-and-apache-airflow/);
* If you, as a Data Scientist or an Engineer, are able to rapidly prototype a working Proof-Of-Concept, it then becomes easier to convince others within the company about the value that can be created. Even in case the company does have both Data Scientists and Data Engineers, either of the two might not be available at that time due to other priorities. This makes it a valuable asset to be able to do both;
* Many companies do not have the funds to hire teams of Data Scientists and Data Engineers. In fact most companies do not handle terabytes of data on a daily basis and/or streaming data (Big data), so data processing is often at a much smaller scale or slower.

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/DSpyramid.PNG" width="300" height="200">
<sup>source: sensecorp.com</sup>
<br/>

#### 2. Advantages of working with Airflow
Working with Airflow provides you with a number of advantages as opposed to for instance working with more traditional cron jobs:
* It has good facilities with respect to error handling, including upstream errors (dependencies);
* It facilitates backfilling of historical data;
* Monitoring / logging facilities;
* A large user group contributing by building standard operators, enabling connections to many other infrastructures;
* Airflow has extensive support for AWS and GCP and to a lesser extent for Azure (Hook, Sensor and Operator for Blob Storage and Azure Data Lake), although Databricks that has been integrated in Azure has contributed an Airflow operator which enables submitting runs to the Databricks platform. Hooks, Sensors and Operators are in the contrib section (beta), which can be found at https://github.com/apache/airflow/tree/master/airflow/contrib;
* Integration in the cloud with big data and machine learning. You can build end-to-end (ML) solutions in the cloud with Airflow in combination with the other cloud services;
* Thanks to the above-mentioned advantages, data engineers and data scientists don't waste much time on DevOps.

#### 3. Setting up the Airflow environment in GCP
A prerequisite to setting up an Airflow environment in GCP is that you have a google account (gmail account), with which you can launch Google Cloud Platform (GCP). The nice thing of GCP is that it comes with a free $300,- trial credit.

Then launch your Google cloud console (https://console.cloud.google.com), and navigate to 'Composer' via the 'hamburger' icon in the top left corner. 
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



<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowgraphview.PNG" width="955" height="75">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowvars.png" width="1084" height="214">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerConfig.png" width="820" height="767">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerMenu.PNG" width="774" height="265">
<br/>
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowtreeview.PNG" width="1183" height="647">


#### 4. DAG structure and building a DAG
	
Explain about the DAG.
what is asyclical graph. a pipeline.  Pipelines are designed as a directed acyclic graph by dividing a pipeline into tasks that can be executed independently. Then these tasks are combined logically as a graph.


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



