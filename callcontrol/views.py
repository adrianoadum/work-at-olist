from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PhoneCall
from .serializers import BillingSerializer, PhoneCallSerializer


class PhoneCallViewSet(viewsets.ViewSet):
    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
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
