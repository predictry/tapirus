#Tapirus 
Data tap.

This application collects transactional data from logs and stores them on S3.
It provides an [API](doc/API.md) for data retrieval.

##Configuration
Refer to the [doc file](doc/Configuration.md).


##Data Records
The files generated by tapirus from events have a standardized structure described [here](doc/StandardDataFormat.md)


##API
Refer to the [API doc](doc/API.md)


##Requirements
You need to have:
  - Python 3.4.2+
  - SQL database (MySQL, MariaDB, SQLite)
  
Python specific requirements are in the [requirements.txt](requirements.txt) file.


##Deployment
To run the application, you can a peek at the sample [supervisor](conf/supervisor-app.conf) configuration file.

It runs uWSGI, Redis server, RQ workers, Luigi server, Nginx, and application specific services. All of these dependencies
are downloaded and setup in the Dockerfile. Though you need to have your configuration files on the project's
base path. You can copy the sample files from `conf/` and modify them according to your environment.
You need a SQL database running, with a database created for the application. Just specify this database, along with
connection details in the `datastore` section of the `config.ini` file.

To run the application locally though, you just need the Redis server, an RQ worker, and Luigi server.


##Third Party Services

**AWS-S3**
Tapirus stores processed data in AWS S3. In order to do that, you need to specify configuration details for AWS S3.
There are three fields that are required in the `s3` section of the `config.ini` file:
  - bucket=myBucket: name of S3 bucket, e.g. predictry
  - prefix=path/pattern: path, after the bucket, e.g. data/processed
  - records=records: the name of the folder to store record files
  
This translates into `s3://predictry/data/processed/records/`. For data access, tapirus expects a [boto.cfg](conf/boto.cfg) file with the
proper credentials, in the project's root file for the docker build process.


**Error Reporting**
Tapirus can send errors generated from logs to a restful endpoint for processing. This endpoint is assumed to be a queue/topic
that is capable of receiving at least several hundred messages within a minute or so. An async recipient is ideal.
In any case, this process does not interrupt the processing of logs themselves. It is handled by independent workers,
that consume the errors messages from an internal queue, managed by [RQ](http://python-rq.org/).

 
