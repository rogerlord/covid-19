import datetime
import timeit


def to_date(dt) -> datetime.date:
    if isinstance(dt, datetime.datetime):
        return dt.date()
    if isinstance(dt, datetime.date):
        return dt
    raise Exception(f"Wrong input - expected datetime or date, but was {type(dt)}.")


# Due to Jonathan Kosgei: https://gist.github.com/jonathan-kosgei/a0e3fb78d81f9f3a09778ced6eca7161
def timer(function):
    def new_function():
        start_time = timeit.default_timer()
        function()
        elapsed = timeit.default_timer() - start_time
        print('Function "{name}" took {time} seconds to complete.'.format(name=function.__name__, time=elapsed))

    return new_function()
