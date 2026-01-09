# =============================================================================
# models.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   Models for D-Tools SI and CRM API integration. Defines database schema for
#   storing API payloads and related metadata.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

from django.db import models

# Create your models here.
class SendToSI(models.Model):
    # Fields
    Deal_Name = models.JSONField()
    Deal_ID = models.JSONField()
    Mission_ID = models.JSONField()
    Progress = models.JSONField()
    Account_Name = models.JSONField()

    AllFields = [Deal_Name, Deal_ID, Mission_ID, Progress, Account_Name]

    def __str__(self):
        return str(self.AllFields)
    
class SendToCRM(models.Model):
    # Fields
    ApiKey = models.CharField(max_length=255)
    Type = models.CharField(max_length=50)
    Module = models.CharField(max_length=50)
    Ids = models.JSONField()
    UpdatedOn = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.Module} - {self.Type} - {self.UpdatedOn}"
    