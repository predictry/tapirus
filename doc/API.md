#API

This doc defines the API for requesting data files.

##Endpoints

Legend:
  - []: Indicates format of parameter
  - {}: Indicates value range of parameter

|Endpoint|Purpose|Parameters|
|--------|-------|----------|
|/data-files|Request a data file for specific date hour|  **date**: date of record [yyyy-mm-dd] for file; <br/> **hour**: hour of record [hh]{1-24}|
|/data-files/interval|Request data files for specific  date hour range| **startDate**: start date of records [yyyy-mm-dd] <br/> **endDate**:end date for records [yyyy-mm-dd] <br/> **startHour**: starting hour of records [hh]{1-24}<br/> **endHour**: end hour of records [hh]{1-24}|
|/timeline|Information about available records|None|


##Record Status

|Flag|Description|Meaning|
|-----|--------------|----------|
|**NOT_FOUND**|Not Found|There are no archives for the Record.|
|**PENDING**|Pending|Archives are being downloaded.|
|**DOWNLOADED**|Downloaded|Archives have been downloaded.|
|**BUILDING**|Building|Archives are being parsed, and compressed into one file.|
|**PROCESSED**|Processed|Compressed file has been uploaded to repository, and a valid URI is available.|
