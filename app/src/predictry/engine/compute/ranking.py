__author__ = 'guilherme'

from collections import Counter
from operator import itemgetter


def rank_most_popular_items(data, key, collection=False, n=5):

    allItems = []

    for x in data:
        if collection:
            allItems.extend(x[key])
        else:
            allItems.append(x[key])

    counter = Counter(allItems)

    itemsrank = []
    for i in counter.most_common(n):
        itemsrank.append({"id": i[0], "matches": i[1]})

    return sorted(itemsrank, key=itemgetter("matches"), reverse=True)