from django.contrib import admin
from .models import fileQueue, positiveTerm, negativeTerm, restrictionTitle, restrictionTerm, processingData, infoFieldCategory, infoFieldArray,flaggedRestriction,flaggedSentence

# Register your models here.
admin.site.register(fileQueue)
admin.site.register(positiveTerm)
admin.site.register(negativeTerm)
admin.site.register(restrictionTitle)
admin.site.register(restrictionTerm)
admin.site.register(processingData)
admin.site.register(infoFieldCategory)
admin.site.register(infoFieldArray)
admin.site.register(flaggedRestriction)
admin.site.register(flaggedSentence)