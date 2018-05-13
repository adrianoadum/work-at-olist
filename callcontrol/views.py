from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .billing import Billing
from .models import PhoneCall
from .serializers import BillingSerializer, PhoneCallSerializer


class PhoneCallViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    create:
    Record a phone call register.
    """
    queryset = PhoneCall.objects.all()
    serializer_class = PhoneCallSerializer


class BillingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = PhoneCall.objects.all()
    serializer_class = BillingSerializer

    def list(self, request, *args, **kwargs):
        """
        Generate a monthly phone bill for a specified number.

        ``phone_number`` is **required**.

        ``period`` is optional. Default is the last closed month. Expected
        format is *MM/YYYY*
        """
        serializer = BillingSerializer(data=request.query_params)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')
            period = serializer.validated_data.get('period')
            return Response(Billing.create_bill(phone_number, period))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
