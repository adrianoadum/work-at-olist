"""
Module responsible for billing calculations.
"""
from dateutil.rrule import DAILY, rrule
from django.utils import timezone

from .models import Pricing
from .utils import time_in_range


def calculate_call_price(start, end):
    """
    Calculate call price based on period.
    """
    if end <= start:
        return 0

    pricing_rules = Pricing.objects.all()

    call_price = 0
    standing_price = None
    for pricing in pricing_rules:
        # check current loop refers to standing price
        start_in_range = time_in_range(
            pricing.period_start, pricing.period_end, start.time())
        if not standing_price and start_in_range:
            standing_price = pricing.standing_price

        # in case of 24h+ call, calculate each day separately
        for loop_date in list(rrule(DAILY, dtstart=start, until=end)):
            charge_loop_period_start = loop_date.replace(
                hour=pricing.period_start.hour,
                minute=pricing.period_start.minute,
                second=pricing.period_start.second,
                microsecond=pricing.period_start.microsecond,
            )
            charge_loop_period_end = loop_date.replace(
                hour=pricing.period_end.hour,
                minute=pricing.period_end.minute,
                second=pricing.period_end.second,
                microsecond=pricing.period_end.microsecond,
            )

            if charge_loop_period_end < charge_loop_period_start:
                charge_loop_period_end += timezone.timedelta(days=1)

            period_day_start = max(start, charge_loop_period_start)
            period_date_end = min(end, charge_loop_period_end)

            if period_day_start > period_date_end:
                continue

            period_to_charge = period_date_end - period_day_start
            minutes_to_charge = int(period_to_charge.seconds / 60)

            call_price += pricing.price_per_minute * minutes_to_charge

    if not standing_price:
        raise RuntimeError('Failed to define Standing Price')

    call_price += standing_price

    return call_price