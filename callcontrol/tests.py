from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import PhoneCall


class CallStartTestCase(APITestCase):
    def test_call_start(self):
        """
        Ensure we can start a new phone call record.
        """
        url = reverse('phonecall-list')
        data = {
            'id': 1,
            'type': 'start',
            'timestamp': '2016-02-29T12:00:00Z',
            'call_id': 1,
            'source': '99988526423',
            'destination': '9993468278'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhoneCall.objects.count(), 1)
        self.assertEqual(PhoneCall.phonecallrecord_set.count(), 1)
