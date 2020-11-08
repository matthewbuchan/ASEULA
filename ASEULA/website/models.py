from django.db import models

# Create your models here.
class softwareIndex(models.Model):
    softwarename = models.CharField(max_length=30)    
    publishername = models.CharField(max_length=30,blank=True, null=True)
    informationurl = models.CharField(max_length=50,blank=True, null=True)
    flaggedrestrictions = models.TextField(blank=True, null=True)    
    checkdate = models.DateTimeField(blank=True, null=True)
    checkby = models.CharField(max_length=50,blank=True, null=True)

    def __str__(self):
        return self.softwarename
    