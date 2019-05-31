# Source: https://gist.github.com/adah1972/f4ec69522281aaeacdba65dbee53fade
from collections import namedtuple
import functools
import json
import six
import gevent.time


def override(func):
    """Unnecessary, non-pythonic boilerplate, will be removed."""
    return func


def timeit(method):
    time_func = gevent.time.time

    def timed(*args, **kw):
        start_time = time_func()
        result = method(*args, **kw)
        print('\t[@timeit] ', method.__name__, time_func() - start_time)
        return result

    return timed


def memoize(func):
    '''Decorator which enables caching function's return values when called with the exact same arguments.

    When decorated function is called with arguments that are already in cache (key exists) it won't be executed
    but cached value will be returned instead. All arguments are serlialized into a single string.

    Cached values can be inspected by: print(decorated_func.cache)

    Note:
    This is extremely rare and probably won't be exploited by accident :)
    1) key = basic_key
        foo(True) and foo('True') are cached under same key name
    2) key = bulletproof_key
        foo(True) and foo('True') will be treated separately (different key in dict)
    '''
    cache = func.cache = {}

    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        basic_key = str(args) + str(kwargs)
        cls_name = lambda val: val.__class__.__name__
        bulletproof_key = basic_key + str([cls_name(arg) for arg in args]) + \
            str([cls_name(val) for val in kwargs.values()])
        key = bulletproof_key
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return memoized_func
