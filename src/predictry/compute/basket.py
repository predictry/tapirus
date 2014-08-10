__author__ = 'guilherme'

from collections import Counter
from operator import itemgetter


def rank_most_popular_items(collections, key, n=5):

    #find items that pop up the most
    allItems = []

    for collection in collections:
        allItems.extend(collection[key])

    counter = Counter(allItems)

    itemsrank = []
    for i in counter.most_common(n):
        itemsrank.append({"id": i[0], "score": i[1]})

    return sorted(itemsrank, key=itemgetter("score"), reverse=True)
