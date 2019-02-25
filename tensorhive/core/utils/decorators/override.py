'''
It only wraps decorated function and HAS NO EFFECT at all.
Use @override decorator in order to increase readability and
make inheritance mechanism more visible.
'''


def override(func):
    return func
