# =============================================================================
# serializers.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   Serializers for D-Tools SI and CRM API models. Used for converting model
#   instances to and from JSON for RESTful endpoints.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

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