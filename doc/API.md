#API

This doc defines the API for requesting data files.

##Endpoints

Legend:
  - []: Indicates format of parameter
  - {}: Indicates value range of parameter

|Endpoint|Purpose|Parameters|
|--------|-------|----------|
|/records|Request a data file for specific date hour|  **date**: date of record [yyyy-mm-dd] for file; <br/> **hour**: hour of record [hh]{0-23}; <br/> **tenant: Tenant Id**|
|/records/interval|Request data files for specific  date hour range| **startDate**: start date of records [yyyy-mm-dd] <br/> **endDate**:end date for records [yyyy-mm-dd] <br/> **startHour**: starting hour of records [hh]{0-23}<br/> **endHour**: end hour of records [hh]{0-23}; <br/> **tenant: Tenant Id**|
|/records/timeline|List of records, organised in a timeline|**skip**: number of records to skip <br/> **limit**: number of records to return <br/> **reverse**: Returns from earliest to most recent when set to *True*; <br/> **tenant: Tenant Id**|

##Data Structures

###Record
```javascript
{
	"date": "Date of record => YYYY-MM-DD:str",
	"hour": "Hour of record => hh: int",
	"status": "Record status: {described below} => str",
	"record_files": [{"tenant": "str", "uri": "URI of record on S3 => str"}],
	"last_updated": "Timestamp of when the record was last updated => ISO8601:YYYY-MM-DD HH:MM:SS:str"	
}
```

###Records: /records/interval

```javascript
{
  "count": "Number of records returned => int",
  "metadata": {
    "endDate": "Date of latest record returned => YYYY-MM-DD:str",
    "endHour": "Hour stamp of latest record returned => hh:int",
    "startDate": "Date of earliest record returned => YYYY-MM-DD:str",
    "startHour": "Hour stamp of earliest record returned => hh:int"
    "tenant": "Tenant Id if provided, * otherwise."
  },
  "records": [List of Records => Record]
}
```

###Records: /records/timeline

```javascript
{
  "count": "Number of records returned => int",
  "metadata": {
	  "timeline": {
		  "start": {
			  "date": "Date of earliest record returned => YYYY-MM-DD:str",
			  "hour": "Hour stamp of earliest record returned => hh:int"
		  },
		  "end": {
			  "date": "Date of latest record returned => YYYY-MM-DD:str",
			  "hour": "Hour stamp of latest record returned => hh:int"		  
		  }
	  },
	  "count": "Number of records returned => int",
	  "total": "Total number of records => int",
	  "tenant": "Tenant Id if provided, * otherwise."
  },
  "records": [List of Records => Record]
}
```

##Record Status

|Flag|Description|Meaning|
|-----|--------------|----------|
|**NOT_FOUND**|Not Found|There are no archives for the Record.|
|**PENDING**|Pending|Archives are being downloaded.|
|**DOWNLOADED**|Downloaded|Archives have been downloaded.|
|**BUILDING**|Building|Archives are being parsed, and compressed into one file.|
|**PROCESSED**|Processed|Compressed file has been uploaded to repository, and a valid URI is available.|