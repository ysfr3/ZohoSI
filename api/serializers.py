from rest_framework import serializers
from .models import SendToSI, SendToCRM

class StringBoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendToSI
        fields = '__all__'

class CRMSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendToCRM
        fields = '__all__'