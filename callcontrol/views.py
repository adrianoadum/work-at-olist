from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PhoneCall
from .serializers import BillingSerializer, PhoneCallSerializer


class PhoneCallViewSet(viewsets.ViewSet):
    """
    Phone call control.
    Used to send call detail records.
    """
    def list(self, request):
        phone_calls = PhoneCall.objects.all()
        serializer = PhoneCallSerializer(phone_calls, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = PhoneCallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillingViewSet(viewsets.ViewSet):
    """
    Generates bill for given phone number.
    Period is optional, default is the previous month from now.
    """
    def list(self, request):
        serializer = BillingSerializer(data=request.query_params)
        if serializer.is_valid():
            return Response(
                serializer.generate_billing(serializer.validated_data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
