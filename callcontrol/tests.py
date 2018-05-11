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
        Create started phone call.
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


class GenerateBillTestCase(APITestCase):
    def test_generate_bill(self):
        """
        Ensure we can create bill.
        """
        url = reverse('billing-list')
        data = {'phone_number': '99988526423'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BillingCorrectValueTestCase(APITestCase):
    def setUp(self):
        """
        Create two calls.
        """
        url = reverse('phonecall-list')
        for i in range(1, 3):
            data = {
                'type': 'start',
                'timestamp': '2018-05-0%dT21:57:13Z' % i,
                'call_id': i,
                'source': '99988526423',
                'destination': '9993468278'
            }
            self.client.post(url, data, format='json')

            data = {
                'call_id': i,
                'type': 'stop',
                'timestamp': '2018-05-0%dT22:10:56Z' % i,
            }
            self.client.post(url, data, format='json')

    def test_billing_corret_value(self):
        """
        Ensure bill value is correct.
        """
        url = reverse('billing-list')
        data = {'phone_number': '99988526423'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1.08)
