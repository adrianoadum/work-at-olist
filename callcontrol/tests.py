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

    def test_invalid_source_short(self):
        """
        Throw error on short source
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '999885264',
            'destination': '9993468278'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_source_long(self):
        """
        Throw error on long source
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '999885264999',
            'destination': '9993468278'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_source_pattern(self):
        """
        Throw error on wrong source
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '999885-264',
            'destination': '9993468278'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_destination_short(self):
        """
        Throw error on short destination
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '9993468278',
            'destination': '99988526',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_destination_long(self):
        """
        Throw error on long destination
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '9993468278',
            'destination': '999885264999',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_destination_pattern(self):
        """
        Throw error on wrong destination
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '9993468278',
            'destination': '999885-264',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_timestamp(self):
        """
        Throw error on wrong destination
        """
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2016-22-29T12:00:00Z',
            'call_id': 1,
            'source': '9993468278',
            'destination': '9998852641',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CallEndTestCase(APITestCase):
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

    def test_call_end(self):
        """
        Ensure we can end a existing phone call.
        """
        url = reverse('phonecall-list')
        data = {
            'call_id': 1,
            'type': 'end',
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


class BillingCorrectTotalTestCase(APITestCase):
    def setUp(self):
        """
        Create two calls.
        """
        pass

    def test_billing_corret_value(self):
        """
        Ensure bill value is correct.
        """
        url = reverse('phonecall-list')
        for i in range(1, 3):
            data = {
                'call_id': i,
                'type': 'end',
                'timestamp': '2018-04-0%dT22:10:56Z' % i,
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            data = {
                'type': 'start',
                'timestamp': '2018-04-0%dT21:57:13Z' % i,
                'call_id': i,
                'source': '9998852642',
                'destination': '9993468278'
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.data))

        url = reverse('billing-list')
        data = {'phone_number': '9998852642', 'period': '2018-04'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['list']), 2)
        self.assertEqual(response.data['total'], 'R$1,08')


class BillingLongCallTestCase(APITestCase):
    def setUp(self):
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2018-02-28T21:57:13Z',
            'call_id': 1,
            'source': '9998852642',
            'destination': '9993468278'
        }
        self.client.post(url, data, format='json')
        data = {
            'call_id': 1,
            'type': 'end',
            'timestamp': '2018-03-01T22:10:56Z',
        }
        self.client.post(url, data, format='json')

    def test_long_call(self):
        """
        Ensure bill value is correct when a call is 24h+.
        """
        url = reverse('billing-list')
        data = {'phone_number': '9998852642', 'period': '2018-03'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['list']), 1)
        self.assertEqual(response.data['total'], 'R$86,94')


class InvalidPeriodTestCase(APITestCase):
    def setUp(self):
        url = reverse('phonecall-list')
        data = {
            'type': 'start',
            'timestamp': '2018-03-01T22:10:56Z',
            'call_id': 1,
            'source': '9998852642',
            'destination': '9993468278'
        }
        self.client.post(url, data, format='json')
        data = {
            'call_id': 1,
            'type': 'end',
            'timestamp': '2018-02-28T21:57:13Z',
        }
        self.client.post(url, data, format='json')

    def test_hide_invalid_call(self):
        """
        Ensure invalid calls aren't shown in billing
        """
        url = reverse('billing-list')
        data = {'phone_number': '9998852642', 'period': '2018-03'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['list']), 0)
        self.assertEqual(response.data['total'], 'R$0,00')
        self.assertEqual(PhoneCall.objects.count(), 1)
