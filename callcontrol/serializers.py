import re
from django.utils.timezone import datetime

from rest_framework import serializers

from .models import PhoneCall, PhoneCallRecord


class PhoneCallSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        type = data.get('type')
        timestamp = data.get('timestamp')
        call_id = data.get('call_id')
        source = data.get('source')
        destination = data.get('destination')

        # Perform the data validation.
        if not type:
            raise serializers.ValidationError({
                'score': 'This field is required.'
            })
        if type not in ('start', 'end'):
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
        phone_call, __ = PhoneCall.objects.get_or_create(
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

        return phone_call
