"""
Module responsible for billing calculations.
"""
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from django.utils import timezone

from .models import PhoneCall, Pricing
from .utils import format_currency, time_in_range


class Billing:
    """
    Class responsible for billing calculations.
    """
    @staticmethod
    def calculate_call_price(start, end):
        """
        Calculate call price based on period.
        """
        if end <= start:
            return None

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

    @staticmethod
    def create_bill(phone_number, period=None):
        """
        Create bill.
        """
        if not period:
            period = (timezone.now() - relativedelta(months=1)).date()

        # Having dificulties to filter from last record of each type,
        # so I decided filter on code. :(
        priced_calls = PhoneCall.objects.exclude(price=None)

        phone_calls = [
            call for call in priced_calls if call.source == phone_number]

        billing_calls = []
        for phone_call in phone_calls:
            if phone_call.end.year == period.year and \
               phone_call.end.month == period.month:
                billing_calls.append(phone_call)

        total = sum(call.price for call in billing_calls if call.price)

        bill = {
            'subscriber': phone_number,
            'period': period.strftime('%m/%Y'),
            'total': format_currency(total),
            'list': []
        }

        for call in billing_calls:
            bill['list'].append({
                'call_id': call.call_id,
                'destination': call.destination,
                'start_date': call.start.date(),
                'start_time': call.start.time(),
                'duration': str(call.duration),
                'price': format_currency(call.price),
            })

        return bill
