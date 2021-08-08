import datetime


def to_date(dt) -> datetime.date:
    if isinstance(dt, datetime.datetime):
        return dt.date()
    if isinstance(dt, datetime.date):
        return dt
    raise Exception(f"Wrong input - expected datetime or date, but was {type(dt)}.")
