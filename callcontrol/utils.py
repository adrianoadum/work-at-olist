def monthdelta(date, delta):
    """
    Add or subtract months in a spcified date
    """
    month, year = (date.month+delta) % 12, date.year + \
        ((date.month)+delta-1) // 12
    if not month:
        month = 12

    if year % 4 == 0 and not year % 400 == 0:
        min_day = [31, 29]
    else:
        min_day = [28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    day = min(date.day, min_day[month-1])
    return date.replace(day=day, month=month, year=year)
