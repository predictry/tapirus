#Usage

##Resource Endpoints
Note: current base URL is `/predictry/api/`

###Item

| Protocal method | REST API URL  | Descrition  |
|---|---|---|
| POST | /v1/items/?appid={string}&domain={string} | Use this method to create an item | 
| GET | /v1/items/?appid={string}&domain={string}[&q={string}][&priceFloor={float}][&priceCeiling={float}][&tags={string}][&locations={string}][&fields={string}][&limit={int}][&offset={int}] | Use this method to retrive a list of items |
| GET  |  /v1/items/{itemId}/?appid={string}&domain={string}[&fields={string}] | Use this method to retrieve an item
|  PUT | /v1/items/{itemId}/?appid={string}&domain={string} | Use this method to update properties of an item
|  DELETE | /v1/items/{itemId}/?appid={string}&domain={string} | Use this method to delete an item

####Playloads

| Protocal method | REST API URL  | Payload |
|---|---|---|
| POST | /v1/items/?appid={string}&domain={string} | {id:{int}, [name:{string}], [brand:{string}], [model:{string}], [description:{string}],[tags:{string}],[price:{float}], [category:{string}], [subcategory:{string}], [dateAdded:{long}], [itemURL:{string}], [imageURL:{string}], [startDate:{long}], [endDate:{long}], [locations:{string}]|
| PUT | /v1/items/{itemId}/?appid={string}&domain={string} | {[name:{string}], [brand:{string}], [model:{string}], [description:{string}],[tags:{string}],[price:{float}], [category:{string}], [subcategory:{string}], [dateAdded:{long}], [itemURL:{string}], [imageURL:{string}], [startDate:{long}], [endDate:{long}], [locations:{string}]|

###User

| Protocal method | REST API URL  | Descrition  |
|---|---|---|
| POST | /v1/items/?appid={string}&domain={string} | Use this method to create an item | 
| GET | /v1/items/?appid={string}&domain={string}[&q={string}][&priceFloor={float}][&priceCeiling={float}][&tags={string}][&locations={string}][&fields={string}][&limit={int}][&offset={int}] | Use this method to retrive a list of items |
| GET  |  /v1/items/{itemId}/?appid={string}&domain={string}[&fields={string}] | Use this method to retrieve an item
|  PUT | /v1/items/{itemId}/?appid={string}&domain={string} | Use this method to update properties of an item
|  DELETE | /v1/items/{itemId}/?appid={string}&domain={string} | Use this method to delete an item