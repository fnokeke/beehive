import random


def get(group):
    quotes = get_pos_quotes() if int(group) % 2 == 1 else get_neg_quotes()
    random.shuffle(quotes)
    return quotes


def get_pos_quotes():
    return [
        #
        'pos-quote1',
        #
        'pos-quote2',
        #
        'pos-quote3',
        #
        'pos-quote4',
        #
        'pos-quote5',
        #
        'pos-quote6',
        #
        'pos-quote7',
        #
        'pos-quote8',
        #
        'pos-quote9',
        #
        'pos-quote10'
    ]


def get_neg_quotes():
    return [
        'neg-quote1',
        #
        'neg-quote2',
        #
        'neg-quote3',
        #
        'neg-quote4',
        #
        'neg-quote5',
        #
        'neg-quote6',
        #
        'neg-quote7',
        #
        'neg-quote8',
        #
        'neg-quote9',
        #
        'neg-quote10'
    ]
