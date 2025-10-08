import os
from datetime import datetime
from django.shortcuts import render

from dotenv import load_dotenv
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .SIWrapper import SIWrapper
from .CRMWrapper import CRMWrapper
from .models import SendToSI, SendToCRM
from .serializers import StringBoolSerializer, CRMSerializer

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

        SIConnection = SIWrapper()

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

        existingDeal = CRMConnection.get_deal(dealId=dealId)
        print(existingDeal)

        res = CRMConnection.push_new_deal_data(dealId=dealId, data={
            "data": [
                {
                    "id": int(dealId),
                    "dtoolsforzohocrm__D_tools_Project_Id": response.get("ProjectId"),
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

        SI_API = SIWrapper()
        if serializer.validated_data.get("Type") == "Update":
            for id in serializer.validated_data.get("Ids"):
                
                project = SI_API.get_project(project_id=id)
                print(project)
                self.updateCRM(serializer.validated_data, project)

    def updateCRM(self, serialized_data: dict, project_data: dict):
        """
        Update CRM with response from SI

        Args:
            serialized_data (dict): Data from serializer POST request
            response (dict): Response from SI API
        """
        print("updating crm")
        load_dotenv()
        CRMConnection = CRMWrapper()
        dealId = project_data.get("IntegrationProjectId")

        note_content = f"[DEAL UPDATED FROM SI] - Updated On: {str(datetime.now())} - Updated By: {project_data.get("UpdatedBy")}"
        res = CRMConnection.add_note(dealId=int(dealId), note_content=note_content)

        if project_data.get("IsChangeOrder") == "True":
            note_content = f"[Change Order - {project_data.get("CONumber")}] Name: {project_data.get("COName")} | Status: {project_data.get("COStatus")} | Type: {project_data.get("COType")} | Accepted: {project_data.get("COAcceptedOn")} | Rejected: {project_data.get("CORejectedOn")} | Created On: {project_data.get("COCreatedOn")}"
            res = CRMConnection.add_note(dealId=int(dealId), note_content=note_content)

        res = CRMConnection.push_new_deal_data(dealId=int(dealId), data={
            "data": [
                {
                    "id":                 int(dealId),
                    "Amount":             float(project_data.get("Price")),
                    "Labor_Hours":        float(project_data.get("Hours")),
                    "SI_Project_Created": "Yes",
                    "Revision_Number":    str(project_data.get("Revision")),
                    "CO_Number":          str(project_data.get("CONumber")),
                    "Custom_Field01":     project_data.get("CustomField1"),
                    "Custom_Field02":     project_data.get("CustomField2"),
                    "Custom_Field03":     project_data.get("CustomField3"),
                    "Custom_Field04":     project_data.get("CustomField4"),
                    "Custom_Field05":     project_data.get("CustomField5")
                }
            ]
        })

        print(res)