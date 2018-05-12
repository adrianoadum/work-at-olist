import locale
import platform
import re

from dateutil.relativedelta import relativedelta
from django.utils.timezone import datetime
from rest_framework import serializers

from .billing import calculate_call_price
from .models import PhoneCall, PhoneCallRecord


class PhoneCallSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        type = data.get('type')
        timestamp = data.get('timestamp')
        call_id = data.get('call_id')
        source = data.get('source')
        destination = data.get('destination')

        if not type:
            raise serializers.ValidationError({
                'score': 'This field is required.'
            })
        if type not in ('start', 'stop'):
            raise serializers.ValidationError({
                'score': 'Invalid value. Valid values are: "start", "stop".'
            })
        if not timestamp:
            raise serializers.ValidationError({
                'timestamp': 'This field is required.'
            })
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            raise serializers.ValidationError({
                'timestamp': 'Invalid format.'
            })
        if not call_id:
            raise serializers.ValidationError({
                'call_id': 'This field is required.'
            })
        if type == 'start':
            if not source:
                raise serializers.ValidationError({
                    'source': 'This field is required when type is "start".'
                })
            if not destination:
                raise serializers.ValidationError({
                    'destination': 'This field is required when type is "start".'
                })

            pattern = re.compile(r'^\d{10,11}$')
            if not pattern.match(source):
                raise serializers.ValidationError({
                    'source': 'Invalid number format.'
                })
            if not pattern.match(destination):
                raise serializers.ValidationError({
                    'destination': 'Invalid number format.'
                })

        validated_data = {
            'type': type,
            'timestamp': timestamp,
            'call_id': int(call_id)
        }
        if type == 'start':
            validated_data['source'] = source
            validated_data['destination'] = destination

        return validated_data

    def to_representation(self, instance):
        if isinstance(instance, PhoneCall):
            return {
                'call_id': instance.call_id,
                'source': instance.source,
                'destination': instance.destination
            }
        return {
            'call_id': instance.get('call_id'),
            'source': instance.get('source'),
            'destination': instance.get('destination')
        }

    def create(self, validated_data):
        phone_call, __ = PhoneCall.objects.update_or_create(
            call_id=validated_data.get('call_id'),
            defaults={
                'source': validated_data.get('source'),
                'destination': validated_data.get('destination')
            },
        )

        PhoneCallRecord.objects.create(
            call=phone_call,
            type=validated_data.get('type'),
            timestamp=validated_data.get('timestamp'))

        if phone_call.start and phone_call.end:
            phone_call.price = calculate_call_price(
                phone_call.start, phone_call.end)
            phone_call.save()

        return phone_call


class BillingSerializer(serializers.BaseSerializer):
    """
    Serializer responsible to generate bill.
    """

    def to_internal_value(self, data):
        phone_number = data.get('phone_number')
        period = data.get('period')

        if not phone_number:
            raise serializers.ValidationError({
                'phone_number': 'This field is required.'
            })
        pattern = re.compile(r'^\d{10,11}$')
        if not pattern.match(phone_number):
            raise serializers.ValidationError({
                'phone_number': 'Invalid number format.'
            })

        if period:
            try:
                period = datetime.strptime(period, '%Y-%m')
            except ValueError:
                raise serializers.ValidationError({
                    'period': 'Invalid period format.'
                })

            today = datetime.today().replace(day=1)
            if period >= today:
                raise serializers.ValidationError({
                    'period': 'Invalid period.'
                })
        else:
            period = datetime.today().replace(day=1)
            period -= relativedelta(months=1)

        validated_data = {
            'phone_number': phone_number,
            'period': period.date(),
        }

        return validated_data

    @classmethod
    def generate_billing(cls, validated_data):
        """
        Generate Bill.
        """
        phone_calls = PhoneCall.objects.distinct().filter(
            source=validated_data.get('phone_number'),
            phonecallrecord__type='stop',
            phonecallrecord__timestamp__year=validated_data.get(
                'period').year,
            phonecallrecord__timestamp__month=validated_data.get(
                'period').month
        ).exclude(price=None)

        total = sum(call.price for call in phone_calls if call.price)

        if platform.system() == 'Windows':
            locale.setlocale(locale.LC_MONETARY, 'pt-BR')
        else:
            locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

        ret = {
            'subscriber': validated_data.get('phone_number'),
            'period': validated_data.get('period').strftime('%Y-%m'),
            'total': locale.currency(total, grouping=True),
            'list': []
        }

        for call in phone_calls:
            ret['list'].append({
                'destination': call.destination,
                'start_date': call.start.date(),
                'start_time': call.start.time(),
                'duration': str(call.duration),
                'price': locale.currency(call.price, grouping=True),
            })

        return ret
