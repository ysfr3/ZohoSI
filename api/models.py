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
    Equipment_Rev = models.JSONField()
    Cost = models.JSONField()
    Expected_Revenue = models.JSONField()
    Labor_Cost = models.JSONField()
    Labor_Revenue = models.JSONField()
    Labor_Hours = models.JSONField()

    AllFields = [Equipment_Rev, Cost, Expected_Revenue, Labor_Cost, Labor_Revenue, Labor_Hours]

    def __str__(self):
        return str(self.AllFields)