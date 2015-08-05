#Configuration Instructions

All configurations files should be on the base project path, when building the [docker image](../Dockerfile).

##[Tap](https://github.com/predictry/tapirus)

###config.ini
Credentials, service parameters (e.g. execution timeout, db credentials, messaging service channels...)
```ini
[logging]
logconfig=logging.json

[harvester] ;required
threshold=3600
interval=3600
timeout=3600

[datastore] ;required
store=mysql
driver=pymysql
username=user
password=password
host=127.0.0.1
database=appdb

[s3] ;required
bucket=myBucket
prefix=path/pattern.
records=records

[luigi]
configfile=client.cfg

[log-error]
host=127.0.0.1
port=1234
username=user
password=word
topic=log.error
```

[Sample](../conf/config.ini)

###logging.json
Application logging

[Sample](../conf/logging.json)


##[Luigi](https://github.com/spotify/luigi)

###client.cfg
Workflow execution

[Sample](../conf/client.cfg)


##[Nginx](https://github.com/nginx/nginx)
Proxy Server. Fronts uWSGI

###nginx-app.conf
[Sample](../conf/nginx-app.conf)


##[Supervisor](https://github.com/Supervisor/supervisor)
Process execution inside container

###supervisor-app.conf
[Sample](../conf/supervisor-app.conf)


##[uWSGI](https://github.com/unbit/uwsgi)
Web server

###uwsgi.ini
[Sample](../conf/uwsgi.ini)

###uwsgi_params
[Sample](../conf/uwsgi_params)


##[Boto](https://github.com/boto/boto)
AWS interface tools (ec2, s3...)

###boto.cfg

```ini
[Credentials]
region = AWS-REGION
aws_secret_access_key = AWS-SECRET-ACCESS-KEY
aws_access_key_id = AWS-ACCESS-KEY-ID
```