from django.db import models
import os
import re

# Create your models here.
class positiveTerm(models.Model):
    posterm = models.CharField(max_length=20)

    def __str__(self):
        return self.posterm

class negativeTerm(models.Model):
    negterm = models.CharField(max_length=20)

    def __str__(self):
        return self.negterm

class restrictionTitle(models.Model):
    restriction = models.CharField(max_length=40)
    postname = models.CharField(max_length=40)

    def __str__(self):
        return self.restriction

class restrictionTerm(models.Model):
    restriction = models.ForeignKey('restrictionTitle',on_delete=models.CASCADE)
    restrictionterm = models.CharField(max_length=20)

    def __str__(self):
        return self.restrictionterm

class fileQueue(models.Model):
    filefield = models.FileField(upload_to='processing/')
    filename = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        if self.filefield == None:
            pass
        else:
            self.filename = self.__str__()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.filefield.delete()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return os.path.abspath(self.filename)

    def __str__(self):
        return os.path.basename(self.filefield.name)

class processingData(models.Model):    
    filename = models.CharField(max_length=30)
    softwarename = models.CharField(max_length=30)
    publishername = models.CharField(max_length=50,blank=True, null=True)
    informationpage = models.CharField(max_length=50,blank=True, null=True)
    restrictionlist = models.TextField(blank=True, null=True)
    fulldoctext = models.TextField()

    def __str__(self):
        return self.filename
        
class infoFieldCategory(models.Model):    
    categoryname = models.CharField(max_length=30)

    def __str__(self):
        return self.categoryname

class infoFieldArray(models.Model):
    filename = models.ForeignKey('processingData',on_delete=models.CASCADE)
    categoryname = models.ForeignKey('infoFieldCategory',on_delete=models.DO_NOTHING)
    listvalue = models.CharField(max_length=50)

    def __str__(self):
        return self.listvalue

class flaggedRestriction(models.Model):
    filename = models.ForeignKey('processingData',on_delete=models.CASCADE)
    restriction = models.CharField(max_length=80)
    flaggedcolor = models.CharField(max_length=20, default="none")

    def __str__(self):
        return self.restriction

class flaggedSentence(models.Model):
    filename = models.ForeignKey('processingData',on_delete=models.CASCADE)
    restriction = models.ForeignKey('flaggedRestriction',on_delete=models.CASCADE)
    sentence = models.TextField()

    def __str__(self):
        return self.sentence