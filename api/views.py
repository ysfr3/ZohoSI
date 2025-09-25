import os
from django.shortcuts import render

from dotenv import load_dotenv
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .SIWrapper import SIWrapper
from .models import SendToSI
from .serializers import StringBoolSerializer

class PushSendToSI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SendToSI.objects.all()
    serializer_class = StringBoolSerializer

    def perform_create(self, serializer):
        """
        Override perform_create to send data to SI after saving to DB

        Args:
            serializer (Django Serializer): Django Rest Framework Serializer
        """

        serializer.save()
        print(serializer.validated_data)
        self.send_to_si(serializer.validated_data)

    def send_to_si(self, serialized_data: dict):
        """
        Send data from post to SI

        Args:
            serialized_data (dict): Data from serializer POST request
        Returns:
            response (dict): Response from SI API
        """

        load_dotenv()
        token = os.getenv("SI_TOKEN")
        conn = SIWrapper(token=token)
        res = conn.create_project(data={
            "Client": serialized_data.get("Account_Name"),
            "Name": serialized_data.get("Deal_Name"),
            "Progress": serialized_data.get("Progress"),
            "IntegrationProjectId": serialized_data.get("Deal_ID"),
            "Number": serialized_data.get("Mission_ID"),
        })

        print(res)
        self.updateCRM(serialized_data, res)

    def updateCRM(self, serialized_data: dict, response: dict):
        """
        Update CRM with response from SI

        Args:
            serialized_data (dict): Data from serializer POST request
            response (dict): Response from SI API
        """

        pass

class PullSendToSI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SendToSI.objects.all()
    serializer_class = StringBoolSerializer