# =============================================================================
# views.py
# Author: Aidan Lelliott and Jason Owens
# Organization: ASW
# Date: 01/19/2026
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
import json
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

        serializedTemplate = serialized_data.get("SI_Template")
        if serializedTemplate is not None or serializedTemplate != "None":
            passedTemplate = serializedTemplate
        else:
            passedTemplate = None

        print("0-----------------------------------------0")
        print(serializedTemplate)
        print(passedTemplate)
        print("0-----------------------------------------0")


        res = SIConnection.create_project(data={
            "TemplateName": passedTemplate,
            "Client": serialized_data.get("Account_Name"),
            "Name": serialized_data.get("Deal_Name"),
            "Progress": serialized_data.get("Progress"),
            "IntegrationProjectId": serialized_data.get("Deal_ID"),
            "Number": serialized_data.get("Mission_ID"),
            "SalesRep": serialized_data.get("Owner"),
            "ProjectManager": serialized_data.get("Project_Manager"),
            "Designer": serialized_data.get("Engineering_Lead"),
            "CloseDate": serialized_data.get("Closing_Date"),
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
                    "SI_Executed": "Yes",
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
                with open(f"project_{id}.json", "w") as f:
                    f.write(json.dumps(project))
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

        # Initialize labor totals
        techFinalizedLaborHours = 0
        engineeringPostFinalizedLaborHours = 0
        engineeringPreFinalizedLaborHours = 0
        programmingFinalizedLaborHours = 0
        projectManagmentFinalizedLaborHours = 0
        warrantyFinalizedLaborHours = 0
        unassignedFinalizedLaborHours = 0
        travelTimeFinalizedLaborHours = 0
        #travelExpenseFinalizedLaborHours = 0

        # LOOP HERE
        items = project_data.get("Items", [])

        for each_item in items:
            labor_type = each_item.get("LaborType")
            labor_category = None
            hours = 0

            # HARD STOP: exclude items with LaborType = None
            if labor_type is None:
                print(
                    f"[SKIP] LaborType=None excluded | "
                    f"Id={each_item.get('Id')} | "
                    f"LaborTypes={each_item.get('LaborTypes')} | "
                    f"Hours={each_item.get('TotalLaborHours')}"
                )
                continue

            # RULE 1: Phase → use Model + Quantity
            if labor_type == "Phase":
                labor_category = each_item.get("Model")
                hours = each_item.get("Quantity") or 0

            # RULE 2: Non-phase → use LaborTypes + TotalLaborHours
            else:
                labor_category = each_item.get("LaborTypes")
                hours = each_item.get("TotalLaborHours") or 0

            # Skip empty categories safely
            if not labor_category:
                continue

            match labor_category:
                case "Tech Labor":
                    techFinalizedLaborHours += hours
                case "Engineering (Post Sales)":
                    engineeringPostFinalizedLaborHours += hours
                case "Engineering (Pre-Sales)":
                    engineeringPreFinalizedLaborHours += hours
                case "Programming":
                    programmingFinalizedLaborHours += hours
                case "Project Management":
                    projectManagmentFinalizedLaborHours += hours
                case "Warranty":
                    warrantyFinalizedLaborHours += hours
                case "Unassigned":
                    unassignedFinalizedLaborHours += hours
                case "Travel (Time)":
                    travelTimeFinalizedLaborHours += hours
                #case "Travel (Expense)":
                #    travelExpenseFinalizedLaborHours += hours

                case _:
                    print(f"[WARN] Unhandled labor category: {labor_category}")

            # Debug per-item (optional, but useful)
            print(
                f"[DEBUG] LaborType={labor_type}, "
                f"Category={labor_category}, "
                f"Hours={hours}"
            )


        note_content = f"[DEAL UPDATED FROM SI] - Updated On: {str(datetime.now())} - Updated By: {project_data.get("UpdatedBy")}"
        res = CRMConnection.add_note(dealId=int(dealId), note_content=note_content)

        print("\n--- Final Labor Hour Totals ---")
        print(f"Tech Labor:                 {techFinalizedLaborHours}")
        print(f"Engineering (Post Sales):   {engineeringPostFinalizedLaborHours}")
        print(f"Engineering (Pre-Sales):    {engineeringPreFinalizedLaborHours}")
        print(f"Programming:                {programmingFinalizedLaborHours}")
        print(f"Project Management:         {projectManagmentFinalizedLaborHours}")
        print(f"Warranty:                   {warrantyFinalizedLaborHours}")
        print(f"Unassigned:                 {unassignedFinalizedLaborHours}")
        print(f"Travel Time:                {travelTimeFinalizedLaborHours}")
        #print(f"Travel Expense:             {travelExpenseFinalizedLaborHours}")
        #print(f"Warranty Quantity (in Phase): {warrantyQuantityFromPhase}")
        print("--------------------------------\n")
        print(
            f"[DEBUG] LaborType={labor_type}, "
            f"Category={labor_category}, "
            f"Hours={hours}"
        )


        res = CRMConnection.push_new_deal_data(dealId=int(dealId), data={
            "data": [
                {
                    "id":                 int(dealId),
                    #"Amount":             float(project_data.get("Price")),
                    "SI_Realtime_Amount": float(project_data.get("Price")),
                    "Labor_Hours":        float(project_data.get("Hours")),
                    "SI_Executed": "Yes",
                    "Revision_Number":    str(project_data.get("Revision")),
                    "CO_Number":          str(project_data.get("CONumber")),
                    "Custom_Field01":     project_data.get("CustomField1"),
                    "Custom_Field02":     project_data.get("CustomField2"),
                    "Custom_Field03":     project_data.get("CustomField3"),
                    "Custom_Field04":     project_data.get("CustomField4"),
                    "Custom_Field05":     project_data.get("CustomField5"),
                    # These fields need to be filtered and totaled from project items in SI. The get responses below are what they are named in SI
                    "Unassigned_Hours": float(unassignedFinalizedLaborHours),
                    "Tech_Labor_Hours": float(techFinalizedLaborHours),
                    "Eng_Pre_Sales_Hours": float(engineeringPreFinalizedLaborHours),
                    "Eng_Post_Sales_Hours": float(engineeringPostFinalizedLaborHours),
                    "Programming_Hours": float(programmingFinalizedLaborHours),
                    "PM_Hours": float(projectManagmentFinalizedLaborHours),
                    "Travel_Time_Hours": float(travelTimeFinalizedLaborHours),
                    #"Travel_Expense_Misc": float(travelExpenseFinalizedLaborHours),
                    "Warranty_Hours": float(warrantyFinalizedLaborHours),
                }
            ]
        })

        print(res)

@api_view(['GET'])
def delay(request, seconds: int = None):
    """Delay the response for `seconds` seconds and return HTTP 200.

    Accepts the delay value either as a path parameter (e.g. /api/delay/5/) or
    as a query parameter `seconds` (e.g. /api/delay/?seconds=5). Also handles
    query strings like `?5` by inspecting the raw query string.
    """
    s = None
    if seconds is not None:
        s = seconds
    else:
        if 'seconds' in request.GET:
            s = request.GET.get('seconds')
        else:
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

    time.sleep(secs)

    return Response(status=status.HTTP_200_OK)
