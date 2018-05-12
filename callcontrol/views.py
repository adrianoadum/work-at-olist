from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import PhoneCall
from .serializers import BillingSerializer, PhoneCallSerializer

from .billing import create_bill


class PhoneCallViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet responsible for call records.
    """
    queryset = PhoneCall.objects.all()
    serializer_class = PhoneCallSerializer


class BillingViewSet(viewsets.ViewSet):
    """
    Generates bill for given phone number.

    phone_number is required.

    period is optional, default is the previous month from now.
    """
    def list(self, request):
        serializer = BillingSerializer(data=request.query_params)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')
            period = serializer.validated_data.get('period')
            return Response(create_bill(phone_number, period))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
