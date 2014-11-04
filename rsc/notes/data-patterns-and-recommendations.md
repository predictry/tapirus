#Graph db and recommendations
Evaluation of performance of tapirus based on different data patterns present in the database.

## Data models:

Our first data model was:
`user-item`: each user was connected to the item they interacted with.
For the sake of keeping transactions of anonymous users, and grouping user sessions, we changed to:
`user-session-item`: users connect to browsing sessions, and sessions connect to the items the user interacted with in those sessions.

All tests were conducted using the second model, with data from REDMART

## Glossary:
OIV: other items viewed (in other sessions)
OIP: other items purchased (in other sessions)
OIVT: other items viewed together (in the same sessions)
OIPT: other items purchased together (in the same sessions)

## Observations:

**Note**: Test cases #1 & #2 applied non-restricted search, of all items connected to the item of reference.

**OIVT**: we visit multiple sessions connected to the item (2 steps: item-same_session-item)
**OIV**: we visit multiple sessions of all users connected to item (4 steps: item-session-user-other_session-item)


###Test Case #1
Item ID: 5124
Views: 230
Buys: 1494

	OIVT: 55-120ms
	OIPT: 280-390ms
	
	OIV: 820-870ms
	OIP: 5900-6200ms

###Test Case #2
Item ID: 5550
Views: 20
Buys: 341

	OIVT: 50-130ms
	OIPT: 120-200ms
	
	OIV: 2700-3500ms (There are more "other items" viewed by people that viewed this item, compared to item #1)
	OIP: 1900-2020ms

## Hypothesis: 
Recommendation speed is highly dependent on the number of nodes attached to the end of the relationships connecting the node/item in question. Relationships  can be on the same session, or on distant ones.


##Test: 
Let's compare the performance for the top, and least viewed and purchased items

###Top

####Views
	id	matches
	5132	853
	11252	512
	5131	457
	8783	341
	11667	309

####Purchases
	id	matches
	5131	3075
	5132	2610
	11252	1533
	5124	1494
	10431	1392

####Test Case #3
Item ID: 5132 (top views)
Views: 853
Buys: 2610

	OIVT: 55-120ms
	OIPT: 90-160ms
	
	OIV: 1210-1240ms
	OIP: 1400-1500ms

####Test Case #4
Item ID: 5131 (top purchases)
Views: 457
Buys: 3075

	OIVT: 60-170ms
	OIPT: 330-390ms
	
	OIV: 660-730ms
	OIP: 500-900ms 

OIP and OIV is faster for #4 compared to #3, despite having more purchase connections (3532 vs 3463). This is because at the end of each session attached to #3, we have more nodes (items viewed/purchased) to count.


###Bottom
####Views 
	id	matches
	9692	1
	12644	1
	6498	1
	7144	1
	12276	1

####Purchases
	id	matches
	12572	1
	12590	1
	9692	1
	11998	1
	11989	1

####Item Case #5
Item ID: 9692 (one of - least views)
Views: 1
Buys: 1

	OIVT: 30-80ms (single session lookup - only 1 view relationship)
	OIPT: 30-70ms (single session lookup - only 1 purchase relationship)
	
	OIV: 50-100ms (1 session and user in this case)
	OIP: 50-110ms (same)

####Item Case #6
Item ID: 12572 (one of - least purchases)
Views: 5
Buys: 1

	OIVT: 30-50ms (5 sessions lookup, 2 steps to other items)
	OIPT: 30-50ms
	
	OIV: 2700-5400ms (5 sessions lookup as a starting point, 4 steps to the other sessions)
	OIP: 80-110ms

From #5 to #6, OIV look-up speed drastically decreases by a factor of x54, while the number of views relationships branching out from the item only quadrupled. This indicates that we should mindful of the other interactions the users that have interacted with an item X have had.


##Behavior analysis: 
There are 2 factors involved in traversal speed: 
1. Target node distance (number of nodes/relationships to reach it)
2. Number of target nodes in query

For OIVT/OIPT, the target node distance is 1n/2r (1node, 2relationships). Provided that the number of end nodes we'll find in a query is considerably
small, traversal should be relatively quick.
On the other hand, for OIV/OIP, the node distance is 3n/4r (3nodes, 4relationships). This type of traversal if far more affected by the number of target end nodes. Although, even in small numbers, the traversal process can be slow.

Ideally, in the user-item data model, the distance to each target node for OIV/OIP/OIVT/OIPT would always be 1n/2r. This means that both types of traversal (OIVT/OIPT and OIV/OIP) would perform similarly. However, because we would need to check the `session_id` property when performing OIVT/OIPT for each relationship, OIVT/OIPT would take a performance hit, though not as big as OIV/OIP does with the user-session-item model. This was observed in earlier implementations.

Thus, the models user-item and user-session-item offer a trade-off between these two traversals. And in both cases, performance is still highly dependent on the number of target nodes involved in the query (how many other nodes are attached to the end of our look-up?)

The question is whether or not the gains from the user-session-item model, i.e. faster OIVT/OIPT, tracking of anonymous users, outweigh its shortcomings, i.e. slower OIV/OIP. Put it another way, is having faster OIPT/OIVT more relevant than OIV/OIP?

I believe that it is for one reason: 
I see OIV/OIP look-up as being highly analogous to item-to-item collaborative filtering (CF). We are essentially asking the question, "for this particular item X, what other items are most commonly purchased along with it?". 

Finding the answer to this requires us to look-up every item ever purchased by any person that has at least at one time purchased X. We then need to combine all the occurrences of these other purchases (could reach 10,000s),  and sum up each item individually to see which ones pop up the most in our collective basket. 

Although item-to-item CF would count mutual occurrences only, we can see that the only step missing here would be to divide the value we get by the cosine between the 2 vectors that represent the purchase history of each pair of item X for a particular user, to get the actual similarity value. The point here is that the first 2 steps we perform are time consuming enough that they warrant offline computation.

A similar, although different issue exists in traversing "hot items" in the graph databases. Unlike structured tables, it's hard for us to simply
lookup the last 10, 100, or 1,000 entries in a table. Instead, to find the lastest entries for a particular type of action, we must ask the graph to get a hold of every entry of the type (e.g. VIEW), and then rank them based on a specific propery (e.g. timestamp).

With indexing, and proper Java Heap configuration for Neo4j, this can be made more efficient than it sounds. However, it is still much faster to retrieve the exact same information from a structured, auto-incremented table. This tells me that, despite managing relationships well, graphs might not be suitable for real-time recommendation **processing** (stress on the word processing, as opposed to "look-up") for highly dense graphs. Sparse graphs might be a different story, as we've observed with items and users with very few neighbors (See test case #5)

Now, when we consider the fact that we also want to provide real-time analytics to our clients, so that they can see what's happening as it is happening, it's not hard for us to see how improbable that would be with our current scenario. This is why I believe that a counter would be useful. 

A counter would not only keep track of the total number of times a specific action would occur, but would also be able to give us insight on trends such
as whether that number has deviated upward on downward from the average of the previous day or hour, without interrupting other recommendation processes. But this counter would not work alone.

We would create an set of independent, concurrent and cooperative systems (think modules) that would each perform specific tasks: building users' profiles based on their behavior; compute similarity between items based on users' purchasing history; regular house cleaning on the data store; discover new insight from our data and algorithms (think neural networks, and evolutionary computing). 

The only thing we'd need to do, is to take all of this regularly pre-computed information, and to store in such a way that "look-ups" would be all the engine would need to do in *real-time*. It could be in tables, graphs, or a combination of both, with some other NoSQL formula in between. This is what I am currently studying.

##Some very important aspects of the data

The ratio between regular and sporadic baskets is very much dependent on the nature of the site. On stores like REMDART, or Tesco, we could expect more regular purchases, while for stores like Groupon, it would most likely be sporadic. So when we disregarded `session_id` in finding OIV/OIP for REDMART, we almost always had the same result or output as OIVT/OIPT. I suspect that reason was for this is that fact that regular baskets weighed in more than sporadic ones for the store.  For a site such as Groupon though, this approach might not work, which given the apparent volatile nature of its products, a user centered approach might be more effective. In addition to this, when querying data from REDMART, our previous limit of 100 items/actions for post-processing eliminated some of the data, which is probably why results varied only mildly (1 or 2 items). This data could be baskets of other regular users which would give more insight into similar items. This  raises some questions.

####Q1: What is the difference in output between then and now? Could we apply the limit in our new queries? How would it affect results?

Yes, we could apply the same limit of the number of interactions we want to asses in order to find other viewed/purchased items. Although, in cases where neighboring users have many purchases/views, our results would always be biased towards their habits. We observe in the case studies bellow.

**Case studies (OIV):**

*Item: 12572* 
@100 limit
```json
{ "data": { "items": [ { "id": 12734, "score": 8 }, { "id": 11203, "score": 8 }, { "id": 11248, "score": 5 }, { "id": 7821, "score": 4 }, { "id": 12574, "score": 4 }, { "id": 12577, "score": 4 }, { "id": 4777, "score": 4 }, { "id": 5662, "score": 4 }, { "id": 12732, "score": 4 }, { "id": 12737, "score": 4 } ] }, "status": 200 }
```

@200 limit  (1st match changes)
```json
{ "data": { "items": [ { "id": 10447, "score": 9 }, { "id": 12734, "score": 8 }, { "id": 11203, "score": 8 }, { "id": 8350, "score": 6 }, { "id": 12581, "score": 6 }, { "id": 5662, "score": 6 }, { "id": 7250, "score": 6 }, { "id": 9843, "score": 6 }, { "id": 9844, "score": 6 }, { "id": 10449, "score": 5 } ] }, "status": 200 }
```

@300 limit (2nd to 5th matches change)
```json
{ "data": { "items": [ { "id": 10447, "score": 18 }, { "id": 5663, "score": 12 }, { "id": 10026, "score": 12 }, { "id": 10449, "score": 12 }, { "id": 9843, "score": 12 }, { "id": 5662, "score": 10 }, { "id": 9844, "score": 10 }, { "id": 12734, "score": 8 }, { "id": 11203, "score": 8 }, { "id": 6409, "score": 6 } ] }, "status": 200 }
```

@500 limit (1st to 10th matches change)
```json
{ "data": { "items": [ { "id": 11203, "score": 24 }, { "id": 12734, "score": 23 }, { "id": 5662, "score": 18 }, { "id": 10447, "score": 18 }, { "id": 9844, "score": 18 }, { "id": 7821, "score": 12 }, { "id": 12574, "score": 12 }, { "id": 5663, "score": 12 }, { "id": 12577, "score": 12 }, { "id": 4777, "score": 12 } ] }, "status": 200 }
```

*Item: 5124* 
@100 limit
```json
{ "data": { "items": [ { "id": 10367, "score": 100 } ] }, "status": 200 }
```

@200 limit (1st match changes, and we get 9 additional matches)
```json
{ "data": { "items": [ { "id": 9464, "score": 18 }, { "id": 9471, "score": 18 }, { "id": 5132, "score": 10 }, { "id": 7314, "score": 10 }, { "id": 7232, "score": 9 }, { "id": 5346, "score": 9 }, { "id": 6264, "score": 9 }, { "id": 9164, "score": 9 }, { "id": 6918, "score": 9 }, { "id": 5511, "score": 9 } ] }, "status": 200 }
```

@300 limit (1st to 10th matches change)
```json
{ "data": { "items": [ { "id": 9471, "score": 28 }, { "id": 9464, "score": 27 }, { "id": 9164, "score": 14 }, { "id": 6918, "score": 14 }, { "id": 5511, "score": 14 }, { "id": 6505, "score": 14 }, { "id": 5706, "score": 14 }, { "id": 5132, "score": 14 }, { "id": 7314, "score": 14 }, { "id": 11318, "score": 14 } ] }, "status": 200 }
```

@500 limit (7th to 10th matches change)
```json
{ "data": { "items": [ { "id": 9471, "score": 46 }, { "id": 9464, "score": 45 }, { "id": 9164, "score": 23 }, { "id": 6918, "score": 23 }, { "id": 5511, "score": 23 }, { "id": 11173, "score": 23 }, { "id": 6505, "score": 23 }, { "id": 5706, "score": 23 }, { "id": 5132, "score": 23 }, { "id": 7314, "score": 23 } ] }, "status": 200 }
```

The top result changes based on the number of "random" (as in not selected by us) items that we retrieve to compare, thus generating the bias effect from limited real-time evaluation.

**Note** : the queries above are very fast @40-90ms when the values returned are limited to 300 or less, and they take less than 100ms below a limit of 500, which is still considerably faster than before. 

These tests work the same way for OIP, since we're limiting items, not sessions. The question is, how high could we grow our threshold to maintain speed, while using a valid portion of the data to make recommendations; and if we did so use limits, how accurate (and thus effective) would our recommendations be?

As for the difference in output between the user-item and user-session-item model, it all depends on how Neo4j determines which relationships to query first. If there are 10 sessions an item is attached to, and we limit the number of items to 100, Neo4j can either grab 10 items from each of the 10 sessions, or all items from the "first" session, and proceed to the subsequent ones until the quota is filled. Though not studied in detail, I believe the last is in effect.


####Q2: What about limiting users, instead of items/actions or sessions?

We could do that as well. Say we limit our search to 100 users. Incidentally, if each of these users has dozens of sessions, with hundreds of transactions, we'd end up with a slow process. Using a lesser number of users, on the other hand, would give us the bias effect.

This analysis leads us to the think that for finding random relationships between items, graph db can be fast. However, if we seek to find the **most** similar items to a particular one (as in top match), than we're probably better of computing that offline.

The assumption here is that the objective of a recommendation system is to determine what items a user might be interested in, so as to suggest popular, new and interesting options. This, pragmatically, translates to the question of which items are most similar to those he/she is known to be interested in. Similar can be defined differently here, but it's the fundamental metric, regardless of whether we're looking at ratings, views, purchasing history, user-defined preferences, etc.

Also, if we were to pre-compute the similarity between items and store them in the graph in a item-[{similarity score}]-item relationship, it is likely
we'd face the same biasing issue in a dense graph with millions of items. Say for example that we have 50,000 items, and each of them is connected to the other with a similarity score. When we query the database for the most similar items, we'd force the graph to check 49,999 relationships for the value of the similarity score and rank them. 

This is a slow process, as we have observed with the top recent purchases/views/additions to cart recommendation options, which take @5000-9000ms when we limit the number of relationships we query - effectively biasing the result. 

With the entire graph in-memory, we might be able to do this a bit faster. However, in a scenario with 10,000,000 items, loading the whole
graph into memory would be unfeasible, and thus finding the most similar items to 2 or more items at the same time would be an exhaustive and slow query. We'd be better off storing the top matches, say 5-20, to each item in a structured table for fast access. Or we' could create the item-[{similarity score}]-item relationships for 5-20 of each node's top matches only. This would, in my view, make querying data using the graph db much more practical and *accurate*.

author: guilherme@predictry.com
date: 28 August, 2014


