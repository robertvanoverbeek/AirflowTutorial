# Hands-on Airflow Tutorial using Google Cloud Composer

#### 1. Introduction
The aim of this Airflow tutorial is to explain the main principles of Airflow and to provide you with a hands-on working example to get you up to speed with Airflow. Following the definition of Airflow, 'Airflow is a platform to programmatically author, schedule and monitor workflows. Airflow is not a data streaming solution.

I wrote this tutorial as a Data Scientist and I believe many people would say Airflow is a tool for Data Engineers to implement ETL processes. Though, for a number of reasons I believe that being able to perform some Data Engineering tasks as a Data Scientist is a valuable asset:

* With the rise of Cloud providers like AWS, GCP and Azure, which offer a suite of offerings (storage, streaming, Apps, Web, ML), the traditional Data Science pyramid as shown below becomes increasingly vertically integrated. These movements make it easier and faster to create end-to-end solutions in the cloud, even for a small team or as a single person (e.g. https://aws.amazon.com/blogs/machine-learning/build-end-to-end-machine-learning-workflows-with-amazon-sagemaker-and-apache-airflow/). Artificial intelligence, Internet of things and analytics are the upsell technologies for cloud vendors;
* Quite often companies do not have dedicated DS an DE teams, as most companies do not handle terabytes of data on a daily basis and/or streaming data (Big data). Even if they have both, either of the two might not be available at that time due to other priorities. This makes it a valuable asset to be able to do work on both. Besides, if you, as a Data Scientist or an Engineer, are able to rapidly prototype a working Proof-Of-Concept (most likely involving both DE and DS work), it then becomes easier to convince others within the company about the value that can be created.

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/DSpyramid.PNG" width="300" height="200">
<sup>source: sensecorp.com</sup>
<br/>

#### 2. Advantages of working with Airflow
Working with Airflow provides you with a number of advantages as opposed to working with e.g. traditional cron jobs:
* It has good facilities with respect to error handling, including upstream errors (dependencies);
* It facilitates backfilling of historical data;
* Monitoring / logging facilities;
* There is a large user group contributing by building standard operators, enabling connections to many other infrastructures. These can be found on https://github.com/apache/airflow/tree/master/airflow/contrib;
* Integration in the cloud with big data and machine learning. You can build end-to-end (ML) solutions in the cloud with Airflow in combination with the other cloud services;
* With the ease of use data engineers and data scientists don't waste much time on DevOps.

#### 3. Setting up the Airflow environment in Google Cloud Platform (GCP)
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
* Select a location closest to you. For instance europe-west1-d. Check https://cloud.google.com/compute/docs/regions-zones/ if you wnat to know more about server locations;
* Machine type. For this tutorial you may choose the smallest configuration in terms of CPUs;
* Disk size. At the time of writing the minumum is 20GB;
* Python version. Select Python version 3.
* Lastly click 'CREATE'.

After a few minutes you will notice that the creation of the environment has been completed. You will then be able to drill down on it, where you will find the following screen (the option 'node configuration' will become visible if you click 'EDIT'):

<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/ComposerConfig.png" width="820" height="767">
<br/>

The environment comes pre-installed with a number of Python packages, such as:

Pandas, google-cloud-bigquery, google-cloud-dataflow, google-cloud-storage, Pandas-gbq, tensorflow and kubernetes.

When you use the button 'PYPI PACKAGES' you will be able to select more Python packages (more information on: https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies).

In order to deploy a DAG file, drill down on the link DAGs folder. In the following paragraph I will explain how you can deploy the DAG of this repository (contained in the DAG folder of this repository). 

#### 4. DAG structure and building and deploying a DAG
	
With Airflow you can deploy DAGs, which stands for Directed Acyclic graph. This is a finite directed graph with no directed cycles. So it always goes in one direction and does not form a circle. The simple DAG for this tutorial is shown below: 
<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowgraphview.PNG" width="955" height="75">
<br/>
This DAG script of this tutorial demonstrates the usage of Airflow in an ETL process. In this case it periodically Extracts data from some place(public BigQuery dataset stackoverflow.posts_questions) over a certain time period and store it in a certain form (Transform) as csv file (Load). From there it can be made available as data source for i.g. reporting (e.g. very simple with Google's Data Studio) and/or Machine Learning. Side note: If you want to use Power BI in combination with GCP it is better to store and leave the data in BigQuery (which is also a step in the DAG of this tutorial), as this makes securely accessing the data from Power BI easier with the standard BigQuery connector in Power BI. I believe using a csv file stored in GCP for usage in a Power BI is only advisable if you can make the data publicly available, which step is explained in https://cloud.google.com/storage/docs/access-control/making-data-public.

While our DAG is quite simple in terms of processes it posesses some extra features that also highlight some functionalities of Airflow:
* Centrally strored variables;
* Backfilling of historical data;
* The usage of Macros and Jinja Templating.

Generally the structure of an Airflow DAG consists of 5 parts:
1. Importing the modules and declaring variables, including referencing the centrally stored variables;
2. Default arguments;
3. Instantiation of the DAG;
4. The tasks;
5. Dependencies / order of the flow.

I will explain these five steps using our DAG as an example.

##### 4.1 Modules and variables
The code that is part of this step contains amongst other things:
```
from datetime import date, datetime, timedelta
from airflow import DAG
from airflow import models
from airflow.contrib.operators import bigquery_get_data
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

Before we upload the DAG file, we are referencing the centrally stored variables.


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

##### 4.2 Default arguments
lfdsaj
##### 4.3 Instantiation of the DAG
lfdsaj
##### 4.4 The tasks
lfdsaj
##### 4.5 Dependencies / order of the flow



<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowvars.png" width="1084" height="214">
<br/>


<img src="https://github.com/robertvanoverbeek/AirflowTutorial/blob/master/images/airflowtreeview.PNG" width="1183" height="647">




In the code below I will reference to these steps.

For this DAG you need to save key-value pairs in Airflow (via Admin > Variables) for the following items:
* gcp_project - Your Google Cloud Project ID.
* gcs_bucket - The Google Cloud Storage bucket to save the output file to. This also implies you have created such a bucket.
In the code below, at step 1, I will explain how to implement the variables.
Check https://airflow.apache.org/concepts.html#variables if you want more information about Airflow variables.
Check https://cloud.google.com/storage/docs/creating-buckets if you need more information on creating a gcp bucket,
as this is beyond the scope of this Airflow POC example.

Airflow Variables are stored in Metadata Database, so any call to variables would mean a connection to Metadata DB.
Your DAG files are parsed every X seconds. If you use a large number of variable in your DAG could mean you might end
up saturating the number of allowed connections to your database.
To avoid this situation, it is advisable to use a single Airflow variable with JSON value.
For instance this case, under Admin > variables in the UI I will save a key 'dag_xyz_config', with
a a set (replace the values with your project ID and bucket name without the gs:// prefix, as I fill it in below):
{"gcp_project": "ml-test-240115", "gcs_bucket": "airflowbucket_tst"}

Behandel ook macros, zoals timedelta: info gebruiken van:
https://diogoalexandrefranco.github.io/about-airflow-date-macros-ds-and-execution-date/
en
https://airflow.apache.org/macros.html
Misschien beter om bij catchup=True ook 'depends_on_past': True te gebruiken, om te voorkomen dat er teveel taken tegelijk draaien. Ff testen.


context managers and then


step 5/5 Define DAG dependencies / defining the order of the tasks

```
docker run hello-world 
```
to verify that Docker can pull and run images.



