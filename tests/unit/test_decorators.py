from tensorhive.core.utils.decorators import memoize
from unittest.mock import patch
import time

def test_memoize_for_correct_func_call_count():
    @memoize
    def add(x, y):
        # Simulates time-expensive operation
        time.sleep(10)
        return x + y

    @memoize
    def foo(a: dict, b: dict, c: bool) -> bool:
        time.sleep(10)
        return a and b and c

    with patch.object(time, 'sleep') as mocked_sleep:
        [add(1, 2) for _ in range(10)]
        assert mocked_sleep.call_count == 1

        mocked_sleep.call_count = 0
        foo({'a': 1}, {'b': 2}, True)
        foo({'a': 1}, {'b': 2}, 'True')
        assert mocked_sleep.call_count == 2
    

    