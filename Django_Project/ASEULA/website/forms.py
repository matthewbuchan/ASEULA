from django import forms
from processing.models import fileQueue

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = fileQueue
        fields = ('filefield',)