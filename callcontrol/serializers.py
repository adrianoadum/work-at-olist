import re

from django.utils.timezone import datetime
from rest_framework import serializers

from .billing import Billing
from .models import PhoneCall, PhoneCallRecord


class PhoneCallSerializer(serializers.ModelSerializer):
    call_id = serializers.IntegerField(
        min_value=1, required=True,
        help_text='Unique identificator for the call')
    price = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True)
    type = serializers.ChoiceField(
        choices=('start', 'end'), write_only=True,
        help_text='Type of the register. Options are "start" or "end".')
    timestamp = serializers.DateTimeField(
        required=True, write_only=True, help_text='Timestamp of the event.')
    source = serializers.RegexField(
        r'\d{10,11}', max_length=11, min_length=10, required=False,
        help_text=('Required when type is "start". Phone '
                   'number that originated the call.'))
    destination = serializers.RegexField(
        r'\d{10,11}', max_length=11, min_length=10, required=False,
        help_text=('Required when type is "start". Phone '
                   'number that received the call.'))

    def validate(self, data):
        if data['type'] == 'start':
            if not data['source']:
                raise serializers.ValidationError(
                    'This field is required when type is "start"')
            if not data['destination']:
                raise serializers.ValidationError(
                    'This field is required when type is "start"')
        return data

    def create(self, validated_data):
        try:
            phone_call = PhoneCall.objects.get(
                call_id=validated_data.get('call_id'))
        except PhoneCall.DoesNotExist:
            phone_call = PhoneCall(call_id=validated_data.get('call_id'))

        if 'source' in validated_data:
            phone_call.source = validated_data['source']
        if 'destination' in validated_data:
            phone_call.destination = validated_data['destination']

        phone_call.save()

        PhoneCallRecord.objects.create(
            call=phone_call,
            type=validated_data.get('type'),
            timestamp=validated_data.get('timestamp'))

        if phone_call.start and phone_call.end:
            phone_call.price = Billing.calculate_call_price(
                phone_call.start, phone_call.end)
            phone_call.save()

        return phone_call

    class Meta:
        model = PhoneCall
        fields = ('id', 'call_id', 'timestamp', 'type',
                  'source', 'destination', 'price')


class BillingSerializer(serializers.BaseSerializer):
    phone_number = serializers.RegexField(
        r'\d{10,11}', max_length=11, min_length=10, required=True,
        help_text=('Phone number of the bill.'))
    period = serializers.RegexField(
        r'\d{10,11}', max_length=11, min_length=10, required=False,
        help_text=('Period(month/year) of the bill.'))

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
                period = datetime.strptime(period, '%m/%Y').date()
            except ValueError:
                raise serializers.ValidationError({
                    'period': 'Invalid period format.'
                })

            today = datetime.now().replace(day=1).date()
            if period >= today:
                raise serializers.ValidationError({
                    'period': 'Invalid period.'
                })

        validated_data = {
            'phone_number': phone_number,
            'period': period if period else None,
        }

        return validated_data
