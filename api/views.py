# =============================================================================
# views.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   Django REST Framework views for Zoho SI/CRM automation.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

import os
from datetime import datetime
from django.shortcuts import render

from dotenv import load_dotenv
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time
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
                    "SI_Project_Created": "Yes",
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


# Simple delay endpoint for testing/diagnostics
@api_view(['GET'])
def delay(request, seconds: int = None):
    """Delay the response for `seconds` seconds and return HTTP 200.

    Accepts the delay value either as a path parameter (e.g. /api/delay/5/) or
    as a query parameter `seconds` (e.g. /api/delay/?seconds=5). Also handles
    query strings like `?5` by inspecting the raw query string.
    """
    # Determine seconds from path param or query string
    s = None
    if seconds is not None:
        s = seconds
    else:
        # Prefer explicit `seconds` query parameter
        if 'seconds' in request.GET:
            s = request.GET.get('seconds')
        else:
            # Fallback: handle query like `?5` where QUERY_STRING == '5'
            qsraw = request.META.get('QUERY_STRING', '')
            if qsraw.isdigit():
                s = qsraw

    try:
        if s is None or s == '':
            secs = 0
        else:
            secs = int(s)
            if secs < 0:
                raise ValueError("seconds must be non-negative")
    except (TypeError, ValueError):
        return Response({"detail": "Invalid seconds value"}, status=status.HTTP_400_BAD_REQUEST)

    # Perform the delay
    time.sleep(secs)

    return Response(status=status.HTTP_200_OK)
