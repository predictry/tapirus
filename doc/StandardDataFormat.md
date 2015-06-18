#Predictry Computational Systems Std Data Format

This doc defines a standard data format for events, entities in Predictry's computational eco-system.

###Session
```JSON
{
	"id": "string",
	"tenant": "string",
	"timestamp": "string [ISO8601]",
	"fields": "<k: string, v: string>"
}
```

###User
```JSON
{
	"id": "string",
	"tenant": "string",
	"timestamp": "string [ISO8601]",
	"fields": "<k: string, v: string>"
}
```

###Agent
```JSON
{
	"id": "string",
	"tenant": "string",
	"timestamp": "string [ISO8601]",
	"fields": "<k: string, v: string>"
}
```

###Item
```JSON
{
	"id": "string",
	"tenant": "string",
	"timestamp": "string [ISO8601]",
	"fields": "<k: string, v: string>"
}
```


###Action
```JSON
{
	"name": "string",
	"tenant": "string",
	"user": "string",
	"agent": "string",
	"session": "string",
	"item": "string",
	"timestamp": "string [ISO8601]",
	"fields": "<k: string, v: string>"
}
```

##Entities

###User

**Fields**:
```JSON
Client defined
```

###Item
**Fields**:
```JSON
Client defined
```

###Agent
**Fields**:
```JSON
Client defined
```

##Actions

###View
**name**: VIEW
**Fields**:
```JSON
None
```

###Add To Cart
**name**: ADD_TO_CART
**Fields**:
```JSON
{
	"quantity": "int"
}
```

###Started Checkout
**name**: STARTED_CHECKOUT
**Fields**:
```JSON
None
```

###Buy
**name**: BUY
**Fields**:
```JSON
{
	"quantity": "int",
	"sub_total": "float"
}
```


###Search
**name**: SEARCH

**Fields**:
```JSON
{
	"keywords": "string"
}
```

###Delete Item
**name**: DELETE_ITEM

**Fields**:
```JSON
None
```

##Data Record

The data record file is in JSON format. Structure:

```JSON
{
	"metadata": {
		"date": "Date of record logs => YYYY-MM-DD:str",
		"hour": "Hour of record logs => hh:int",
		"processed": "Timestamp of when the log was processed:ISO8601:YYYY-MM-DD HH:MM:SS"
	},
	"sessions": [List of Sessions => Session],
	"agents": [List of Agents => Agent],
	"users": [List of Users => User],
	"items": [List of Items => Item],
	"actions": [List of Actions => Action]
}
```