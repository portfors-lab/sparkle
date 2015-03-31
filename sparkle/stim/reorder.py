import random


def order_function(name):
    if name == 'random':
        return random_order

def random_order(listofthings):
    order = range(len(listofthings))
    random.shuffle(order)
    return order
