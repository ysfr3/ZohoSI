from rest_framework import serializers
from .models import SendToSI

class StringBoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendToSI
        fields = '__all__'