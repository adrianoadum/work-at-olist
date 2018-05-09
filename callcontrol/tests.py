from django.urls import reverse
from django.utils.timezone import datetime
from rest_framework import status
from rest_framework.test import APITestCase

from .models import PhoneCall, PhoneCallRecord


class CallStartTestCase(APITestCase):
    def test_call_start(self):
        """
        Ensure we can start a new phone call.
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '99988526423',
            'destination': '9993468278'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhoneCall.objects.count(), 1)
        self.assertEqual(PhoneCallRecord.objects.count(), 1)


class CallStopTestCase(APITestCase):
    def setUp(self):
        """
        setUp creating started phone call.
        """
        phone_call = PhoneCall.objects.create(
            call_id=1,
            source='99988526423',
            destination='9993468278'
        )
        PhoneCallRecord.objects.create(
            call=phone_call,
            type='start',
            timestamp=datetime.strptime(
                '2016-02-29T12:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        )

    def test_call_stop(self):
        """
        Ensure we can stop a existing phone call.
        """
        url = reverse('phonecall-list')
        data = {
            'call_id': 1,
            'type': 'stop',
            'timestamp': '2016-02-29T14:00:00Z',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhoneCall.objects.count(), 1)
        self.assertEqual(PhoneCallRecord.objects.count(), 2)
