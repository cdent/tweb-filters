"""
A simple demonstration plugin that shows how to extend the TiddlyWeb
filter system.

We'll build one that makes it possible to select and sort tiddlers based
on the number of tags the tiddlers have. For example select=ctags:4
would get those tiddlers that have four tags. select=ctags:>3 would get
those that have more than three tags. And sort=-ctags would return the
tiddlers ordered by number of tags.
"""

from tiddlyweb.filters.select import ATTRIBUTE_SELECTOR
from tiddlyweb.filters.sort import ATTRIBUTE_SORT_KEY


# all plugins get an init method, even if not used
def init(config):
    pass


def tag_count(attribute):
    """
    Return the length of the tags or
    the value of the sort we are doing.
    """
    try:
        return int(attribute)
    except TypeError:
        return len(attribute)


def by_tag_count(entity, attribute, value):
    """
    Return true if the number of tags is value.
    """
    return tag_count(entity.tags) == int(value)


ATTRIBUTE_SORT_KEY['tags'] = tag_count
ATTRIBUTE_SELECTOR['tags'] = by_tag_count


def run_tests():
    import shutil
    try:
        shutil.rmtree('store')
    except:
        pass
    from tiddlyweb.config import config
    from tiddlywebplugins.utils import get_store
    from tiddlyweb.model.bag import Bag
    from tiddlyweb.model.tiddler import Tiddler
    from tiddlyweb.control import filter_tiddlers
    store = get_store(config)
    bag = Bag('place')
    store.put(bag)

    for number in range(5):
        tiddler = Tiddler('tiddler %s' % number, 'place')
        tiddler.text = 'text %s' % number
        for tag in range(number):
            tiddler.tags.append('tag %s' % tag)
        store.put(tiddler)

    tiddlers = list(store.list_bag_tiddlers(bag))
    assert len(tiddlers) == 5

    environ = {'tiddlyweb.store': store}

    sorts = list(
            store.get(tiddler)
            for tiddler in filter_tiddlers(
                tiddlers, 'sort=-tags', environ=environ))
    assert len(sorts[0].tags) == 4
    assert len(sorts[4].tags) == 0

    selected = list(
            store.get(tiddler)
            for tiddler in filter_tiddlers(
                tiddlers, 'select=tags:4', environ=environ))
    assert len(selected) == 1
    assert len(selected[0].tags) == 4

    selected = list(
            store.get(tiddler)
            for tiddler in filter_tiddlers(
                tiddlers, 'select=tags:1', environ=environ))
    assert len(selected) == 1
    assert len(selected[0].tags) == 1

    selectsort = list(
            store.get(tiddler)
            for tiddler in filter_tiddlers(
                tiddlers, 'select=tags:>2;sort=-tags', environ=environ))
    assert len(selectsort) == 2
    assert len(selectsort[0].tags) == 4
    assert len(selectsort[1].tags) == 3


if __name__ == '__main__':
    run_tests()
