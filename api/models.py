from django.db import models

# Create your models here.
class SendToSI(models.Model):
    Deal_Name = models.JSONField()
    Deal_ID = models.JSONField()
    Mission_ID = models.JSONField()
    Progress = models.JSONField()
    Account_Name = models.JSONField()

    AllFields = [Deal_Name, Deal_ID, Mission_ID, Progress, Account_Name]

    def __str__(self):
        return str(self.AllFields)