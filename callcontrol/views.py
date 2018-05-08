from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PhoneCall
from .serializers import PhoneCallSerializer


@api_view(['GET', 'POST'])
def phonecall_list(request):
    """
    List all code phone calls, or create a new one.
    """
    request.body
    if request.method == 'GET':
        phone_calls = PhoneCall.objects.all()
        serializer = PhoneCallSerializer(phone_calls, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PhoneCallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
