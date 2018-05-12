import datetime


def time_in_range(start, end, time_to_check):
    """
    Return True if time_to_check is in the range [start, end]
    """
    if not isinstance(start, datetime.time):
        raise TypeError('"start" must be "time" object')
    elif not isinstance(end, datetime.time):
        raise TypeError('"end" must be "time" object')
    elif not isinstance(time_to_check, datetime.time):
        raise TypeError('"time_to_check" must be "time" object')

    if start <= end:
        return start <= time_to_check <= end
    return start <= time_to_check or time_to_check <= end


def format_currency(value):
    """
    Try to format value as brazilian cash "Real".
    """
    try:
        return ("R$%.2f" % value).replace('.', ',')
    except TypeError:
        return value
