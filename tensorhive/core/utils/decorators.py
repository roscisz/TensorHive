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


Serialized = namedtuple('Serialized', 'json')
def hashable_cache(cache):
    def hashable_cache_internal(func):
        def deserialize(value):
            if isinstance(value, Serialized):
                return json.loads(value.json)
            else:
                return value

        def func_with_serialized_params(*args, **kwargs):
            _args = tuple([deserialize(arg) for arg in args])
            _kwargs = {k: deserialize(v) for k, v in six.viewitems(kwargs)}
            return func(*_args, **_kwargs)

        cached_func = cache(func_with_serialized_params)

        @functools.wraps(func)
        def hashable_cached_func(*args, **kwargs):
            _args = tuple([
                Serialized(json.dumps(arg, sort_keys=True))
                if type(arg) in (list, dict) else arg
                for arg in args
            ])
            _kwargs = {
                k: Serialized(json.dumps(v, sort_keys=True))
                if type(v) in (list, dict) else v
                for k, v in kwargs.items()
            }
            return cached_func(*_args, **_kwargs)
        hashable_cached_func.cache_info = cached_func.cache_info
        hashable_cached_func.cache_clear = cached_func.cache_clear
        return hashable_cached_func

    return hashable_cache_internal
