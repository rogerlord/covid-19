import datetime
from functools import wraps
from time import time


def to_date(dt) -> datetime.date:
    if isinstance(dt, datetime.datetime):
        return dt.date()
    if isinstance(dt, datetime.date):
        return dt
    raise Exception(f"Wrong input - expected datetime or date, but was {type(dt)}.")


# Due to JBirdVegas: https://stackoverflow.com/questions/51503672/decorator-for-timeit-timeit-method/51503837#51503837
def timer(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            end_ = (end_ if end_ > 0 else 0) / 1000.0
            print('Function "{name}" took {time} seconds to complete.'.format(name=func.__name__, time=end_))
    return _time_it
