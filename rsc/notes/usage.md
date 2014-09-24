#Usage

##Version
Beta 0.1.13

##Convention

With the exception of fields that are surrounded by `[]`, all fields specified in either the `URL` or `JSON payload` are required for each request.
A non-specific variable of any data type is represented with the symbolr `x:`. So `[x:]` means an optional parameter of any data type.

##Data Types
Currently, we support the following data types:
```python
boolean
byte
short
int
float
long
double
char
string
```
These values can be primitives, or in lists/arrays. You can have a look at the [Neo4j documentation][1] for details

##A Note on Output

All API calls return the same structured output, provided that the values for each field are set:

```json
{
    "data": {object},
    "error": {string},
    "message": {string},
    "status": {int}
}
```

The `status` field has the HTTP status code of the request. The field `error` has a basic error message (e.g. "404 Not found"), while the field `message` has a more detailed explanation of the error (e.g. "Resource item with given properties was not found").

The `data` object has fields that are specific to each request. For example, if we make a successful `GET` request to retrieve a list of `items` with their id, and price fields, the output should look like the following:

```sh
 curl -X GET "http://api.predictry.com/v1/items/?appid=myappid&domain=myorg&fields=id,price&limit=3"
```

```json
{
    "data": {
        "items":[
            {"id": 1, "price": 14.5},
            {"id": 2, "price": 27.5},
            {"id": 2, "price": 8.95}
        ]
    },
    "status": 200
}
```

Since the were no errors in the request, neither the field `error` nor `message` are returned.

##Authentication
We use Basic HTTP Auth. You should get the username and password for the system administrators.

----------


##Making Recommendations

Tapiru's recommendations are based on users' activity. The engine essentially transverses a client's data domain in a database, looking for similarity between its users' based on their purchasing history. For example, it can look for products that were most viewed by people who also viewed a  product that we're currently viewing. These searches can be delimited by certain parameters, like the price of the products involved in those actions. 

There are 3 types of recommendations:

- Item-based
- User-based
- Trend-based

The recommendation searches above can be limited to transcations that took place at the same time (items bought or viewed together), or historically. To interact with the API using the filters and recommendation options available, see the next section.

###Recommendation
| Protocol method | REST API URL  | Description  |
|---|---|---|
| GET | /v1/recommend/?appid={string}&domain={string} type:{string}, [item_id:{int}], [user_id:{int}], [fields:{string}], [limit:{int}]| Use this method to get a recommendation | 

**Note on protocol:** We use GET to make caching of requests easier.  Relationships between items do not change regularly over time, and thus caching can give high benefits here. The cache can be tweaked to adjust for cases such as "recently top selling" items.

####Recommendation Types
| Recommendation Type | Code  | Description | Required Parameters
|---|---|---|---|
| Other items viewed | type=oiv | What other items were most **viewed** by people that **viewed** x, on another occasion?| itemd_id
| Other items viewed together | type=oivt | What other items were most **viewed** together, by people that **viewed** x?| item_id
| Other items purchased | type=oip | What other items were most **purchased** by people that **purchased** x, on another occasion?| item_id
| Other items purchased together | type=oipt | What other items were most **purchased** together, by people that **purchased** x?| item_id
| Top recent views | type=trv | What items have been **viewed** the most recently? | none
| Top recent purchases | type=trp | What items have been **purchased** the most recently? | none
| Top recent additions to cart | type=trac | What items have been **added to cart** the most recently? | none
| User's top recent views | type=utrv | What items have been **viewed** the most by a particular user recently? | user_id
| User's top recent purchases | type=utrp | What items have been **purchased** the most by a particular user recently? | user_id
| User's top recent additions to cart | type=utrac | What items have been **added to cart** the most by a particular user recently? | user_id
| User's unacquired interests | type=uacnp | What items have been **viewed** but not purchased by a particular user recently? | user_id
| User's recent abandoned items | type=uacnp | What items have been **added to cart** but not purchased by a particular user recently? | user_id

####Filtering
To narrow search results, we can apply filters. Virtually, any property of an item, or user, can be used to filter recommendation results. However, this is not applicable to every type of recommendation. As of v0.1.12, only item-based recommendations support filtering. 
To filter recommendation results, we use special parameter `q`. The structure of a single filter is as follows: `variable$op$value$type$ls`

- **variable**: name of the item property against which the  filter will be applied
- **op**: operation to apply on property, i.e.: *e, gt, lt, gte, lte, cti, ncti*
- **value**: value to be used in operation
- **type**: data type of the item's property, and also `value` parameter, i.e.: *bool, num, str, date (unix timestamp)*
- **ls**: present if the `value` parameter is a list, and absent otherwise

#####Example #1, Single filter: price
```json
q=price$lt$100$num
```

#####Example #2, Single filter: tags
```json
q=tags$cti$electronics$str
```

#####Example #3, Single filter, list: tags
```json
q=tags$cti$electronics,phone$str$ls
```

#####Example #4, Multiple filters: price and tags
```json
q=price$lt$2200$num|tags$cti$electronics,phone$str$ls
```

##Resource Endpoints

The resource endpoints are used to store, and if necessary, read, update and delete data on users, items, and their actions.

###Item

| Protocol method | REST API URL  | Description  |
|---|---|---|
| POST | /v1/items/?appid={string}&domain={string} | Use this method to create an item | 
| GET | /v1/items/?appid={string}&domain={string}[&fields={string}][&limit={int}][&offset={int}] | Use this method to retrieve a list of items |
| GET  |  /v1/items/{item_id}/?appid={string}&domain={string}[&fields={string}] | Use this method to retrieve properties of an item
|  PUT | /v1/items/{item_id}/?appid={string}&domain={string} | Use this method to update properties of an item
|  DELETE | /v1/items/{item_id}/?appid={string}&domain={string} | Use this method to delete an item

####Playloads

| Protocol method | REST API URL  | JSON Payload |
|---|---|---|
| POST | /v1/items/?appid={string}&domain={string} | {id:{int}, [x:]}|
| PUT | /v1/items/{item_id}/?appid={string}&domain={string} | {[x:]}|

###User

| Protocol method | REST API URL  | Description  |
|---|---|---|
| POST | /v1/users/?appid={string}&domain={string} | Use this method to create a user | 
| GET | /v1/users/?appid={string}&domain={string}[&fields={string}][&limit={int}][&offset={int}] | Use this method to retrieve a list of users |
| GET  |  /v1/users/{user_id}/?appid={string}&domain={string}[&fields={string}] | Use this method to retrieve properties of a user
|  PUT | /v1/users/{user_id}/?appid={string}&domain={string} | Use this method to update properties of a user
|  DELETE | /v1/users/{user_id}/?appid={string}&domain={string} | Use this method to delete a user

####Playloads

| Protocol method | REST API URL  | JSON Payload |
|---|---|---|
| POST | /v1/users/?appid={string}&domain={string} | {id:{int}, [email:{string}], [x:]}|
| PUT | /v1/users/{user_id}/?appid={string}&domain={string} | {[email:{string}], [x:]}
        
###Action

| Protocol method | REST API URL  | Description  |
|---|---|---|
| POST | /v1/actions/?appid={string}&domain={string} | Use this method to create an action | 
| GET | /v1/actions/?appid={string}&domain={string}[?type={string}][&fields={string}][&limit={int}][&offset={int}] | Use this method to retrieve a list of actions |
| GET  |  /v1/actions/{action_id}/?appid={string}&domain={string}[&fields={string}] | Use this method to retrieve properties of an action
|  PUT | /v1/actions/{action_id}/?appid={string}&domain={string} | Use this method to update properties of an action
|  DELETE | /v1/actions/{action_id}/?appid={string}&domain={string} | Use this method to delete an action
        
####Playloads

| Protocol method | REST API URL  | JSON Payload |
|---|---|---|
| POST | /v1/actions/?appid={string}&domain={string} | {id:{int}, session_id:{string}, browser_id:{string}, item_id:{int}, type:{string}, [user_id:{int}], [x:]}|
| PUT | /v1/actions/{action_id}/?appid={string}&domain={string} | {[x:]}|


[1]: http://docs.neo4j.org/chunked/stable/graphdb-neo4j-properties.html

Updated: 8 Sep, 2014 @ 11.04AM
Author: guilherme@predicrty.com