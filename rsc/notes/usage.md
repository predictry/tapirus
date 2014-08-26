#Usage

##Version
Beta 0.1.6

##Convention

With the exception of fields that are surrounded by `[]`, all fields specified in either the `URL` or `JSON payload` are required for each request.

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


----------


##Making Recommendations

Tapiru's recommendations are based on users' activity. The engine essentially transverses a client's data domain in a database, looking for similarity between its users' based on their purchasing history. For example, it can look for products that were most viewed by people who also viewed a  product that we're currently viewing. These searches can be delimited by certain parameters, like the price of the products involved in those actions. 

There are 4 options for recommendations, which can essentially be broken into 2:

- What others who viewed x also viewed
- What others who bought x also bought

The recommendation searches above can be limited to transcations that took place at the same time (items bought or viewed together), or historically. To interact with the API using the filters and recommendation options available, see the next section.

###Recommendation
| Protocol method | REST API URL  | Description  |
|---|---|---|
| POST | /v1/recommend/?appid={string}&domain={string} | Use this method to get a recommendation | 

**Note on protocol:** We use POST to generate recomendations, as opposed to GET. The reasoning is that, despite not pushing any data into the database, the process does create a new resource (i.e. recommendation).

####Payload
| Protocol method | REST API URL  | JSON Payload  |
|---|---|---|
| POST | /v1/recommend/?appid={string}&domain={string} | {type:{string}, [item_id:{int}], [user_id:{int}], [fields:{string}], [limit:{int}] | 

####Recommendation Types
| Recommendation Type | Code  | Description |
|---|---|---|
| Other items viewed | type=oiv | What other items were most viewed by people that viewed x?| 
| Other items viewed together | type=oivt | What other items were most viewed together, by people that viewed x?| 
| Other items purchased | type=oip | What other items were most purchased by people that purchased x?| 
| Other items purchased together | type=oipt | What other items were most purchased together, by people that purchased x?| 

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
| POST | /v1/items/?appid={string}&domain={string} | {id:{int}, [x:{int}], [y:{string}], [z:{float}], [k:{long}], [list: array]}|
| PUT | /v1/items/{item_id}/?appid={string}&domain={string} | [x:{int}], [y:{string}], [z:{float}], [k:{long}], [list: array]}|

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
| POST | /v1/users/?appid={string}&domain={string} | {id:{int}, [email:{string}], [x:{int}], [y:{string}], [z:{float}], [k:{long}], [list: array]}|
| PUT | /v1/users/{user_id}/?appid={string}&domain={string} | {[email:{string}], [x:{int}], [y:{string}], [z:{float}], [k:{long}], [list: array]}|
        
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
| POST | /v1/actions/?appid={string}&domain={string} | {id:{int},session_id:{string}, browser_id:{string}, item_id:{int}, type:{string}, [user_id:{int}], [x:{int}], [y:{string}], [z:{float}], [k:{long}], [list: array]}|
| PUT | /v1/actions/{action_id}/?appid={string}&domain={string} | {[x:{int}], [y:{string}], [z:{float}], [k:{long}], [list: array]}|

