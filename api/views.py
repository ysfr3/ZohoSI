import os
from django.shortcuts import render

from dotenv import load_dotenv
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .SIWrapper import SIWrapper
from .CRMWrapper import CRMWrapper
from .models import SendToSI, SendToCRM
from .serializers import StringBoolSerializer, CRMSerializer

kFIELDS = [
    "Price",
    "Notes",
    "Revision",
    "Hours",
    #"ProductCost",
    #"ProductPrice",
    #"LaborCost",
    #"LaborPrice",
]

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
        SIConnection = SIWrapper(token=token)

        res = SIConnection.create_project(data={
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
        
        load_dotenv()
        CRMConnection = CRMWrapper()
        dealId = serialized_data.get("Deal_ID")

        res = CRMConnection.push_new_deal_data(dealId=dealId, data={
            "data": [
                {
                    "id": int(dealId),
                    "dtoolsforzohocrm_D_tools_Project_Id": response.get("ProjectId"),
                }
            ]
        })

        print(res)

class PullSendToSI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SendToSI.objects.all()
    serializer_class = StringBoolSerializer

class PushSendToCRM(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SendToCRM.objects.all()
    serializer_class = CRMSerializer

    def perform_create(self, serializer):
        """
        Override perform_create to send data to CRM after saving to DB

        Args:
            serializer (Django Serializer): Django Rest Framework Serializer
        """

        serializer.save()
        print(serializer.validated_data)
        self.updateCRM(serializer.validated_data)

        SI_API = SIWrapper(token=os.getenv("SI_TOKEN"))

        if serializer.validated_data.get("Type") == "Update" and serializer.validated_data.get("Ids") != []:
            for id in serializer.validated_data.get("Ids"):
                project = SI_API.get_project(project_id=id)
                print(project)
                for field in kFIELDS:
                    if field in project:
                        print(field)
        
    def updateCRM(self, serialized_data: dict):
        """
        Update CRM with response from SI

        Args:
            serialized_data (dict): Data from serializer POST request
            response (dict): Response from SI API
        """
        
        load_dotenv()
        CRMConnection = CRMWrapper(token=os.getenv("CRM_TOKEN"))
        dealId = serialized_data.get("Deal_ID")

        res = CRMConnection.push_new_deal_data(dealId=dealId, data={
            "data": [
                {
                    "id": int(dealId),
                    
                }
            ]
        })

        print(res)