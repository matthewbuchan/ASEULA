from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from processing.models import positiveTerm, negativeTerm, restrictionTitle, restrictionTerm,infoFieldCategory,infoFieldArray,processingData,fileQueue, flaggedRestriction, flaggedSentence
from website.models import softwareIndex
from processing.processfile import *
from django.conf import settings
from .models import softwareIndex
import datetime
import re

# Create your views here.
def Home(request):
        all_documents = fileQueue.objects.all()
        review_docs = processingData.objects.all()
        return render(request, 'main.html', {'Documents' : all_documents, 'PendingReview':review_docs})

def ImportFile(request):
        review_docs = processingData.objects.all()
        filequeue = fileQueue.objects.all()        
        if request.method == "POST":
                if request.FILES:
                        filelist = request.FILES
                        filelisting = request.FILES.getlist('document')
                        postfile = filelist['document']
                        if len(filelisting) >= 2:
                                for items in filelisting:
                                        print(items)
                                        fs=FileSystemStorage()
                                        fs.save("processing/"+ str(items),items)
                                        fileQueue.objects.create(filefield="processing/"+ str(items), filename=items)
                        else:                        
                                fs=FileSystemStorage()
                                fs.save("processing/"+ str(postfile),postfile)
                                fileQueue.objects.create(filefield="processing/"+ str(filelist['document']), filename=request.FILES)
                        return redirect('Home')
                else:
                        pass
        return render(request, 'importfile.html', {'PendingReview':review_docs,'FileQueue':filequeue,})

def ImportText(request):
        review_docs = processingData.objects.all()
        filequeue = fileQueue.objects.all()
        if request.method == 'POST':
                if request.POST.get('document'):
                        usertext = request.POST.get('document')
                        tempfile = str("usertxt" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+ ".txt")
                        f = open(tempfile,mode="w+")
                        f.write(str(usertext))
                        fs = FileSystemStorage()
                        fs.save("processing/"+ str(f.name),f)
                        fileQueue.objects.create(filefield="processing/"+ str(f.name), filename=f.name)
                        f.close()
                        os.remove(tempfile)
                        return redirect('Home')
                else:
                        pass
        return render(request, 'importtext.html', {'PendingReview':review_docs,'FileQueue':filequeue,})

def delete_file(request, pk):
        if request.method == 'POST':
                queuedFile = fileQueue.objects.get(pk=pk)
                queuedFile.delete()
        return redirect('Home')

def ProcessFiles(request):
        posterms = []
        negterms = []
        rxion_dict = {}
        for term in positiveTerm.objects.all():
                posterms.append(term.posterm)
        for term in negativeTerm.objects.all():
                negterms.append(term.negterm)
        for term in restrictionTerm.objects.all():
                if str(term.restriction) in rxion_dict:
                        rxion_dict[str(term.restriction)].append(str(term))
                else:
                        rxion_dict[str(term.restriction)] = []
                        rxion_dict[str(term.restriction)].append(str(term))
        file_list = fileQueue.objects.all()
        jobData = {}
        if file_list:
                for filename in file_list:
                        if processingData.objects.filter(filename__icontains=str(filename)):
                                pass
                        else:
                                #store values from ASEULA Process
                                jobData = AseulaMain("media/processing/" + str(filename),posterms,negterms, rxion_dict)
                                f = fileQueue.objects.get(pk=filename.pk)
                                f.delete()
                                # Populate Database
                                processingData.objects.create(filename=jobData[0], softwarename = jobData[1][jobData[2][0].lower()], publishername=jobData[1][jobData[2][1].lower()], informationpage=jobData[1][jobData[2][2].lower()],restrictionlist=jobData[1][jobData[2][3].lower()],fulldoctext=jobData[6])
                                for item in jobData[2]: 
                                        if infoFieldCategory.objects.filter(categoryname__icontains=item.lower()):
                                                pass
                                        else:
                                                infoFieldCategory.objects.create(categoryname=item.lower())
                                for element in jobData[4]: # Store possible information variables
                                        for item in jobData[4][element]:
                                                infoFieldArray.objects.create(filename=processingData.objects.get(filename=jobData[0]), categoryname=infoFieldCategory.objects.get(categoryname=element), listvalue=item)
                                i=0
                                texthighlight = ["yellow","orange","hotpink","darkkhaki","cyan","goldenrod","springgreen","lightcoral","aquamarine","darksalmon","lightsteelblue","violet"]
                                for category in jobData[5]:
                                        if flaggedRestriction.objects.filter(filename=processingData.objects.get(filename=jobData[0]), restriction__icontains=category.lower()):
                                                pass
                                        else:
                                                flaggedRestriction.objects.create(filename=processingData.objects.get(filename=jobData[0]),restriction=category, flaggedcolor=texthighlight[i])
                                        for sentence in jobData[5][category]:
                                                flaggedSentence.objects.create(filename=processingData.objects.get(filename=jobData[0]), restriction=flaggedRestriction.objects.get(filename=processingData.objects.get(filename=jobData[0]),restriction=category), sentence=sentence)
                                        i += 1
                return redirect('ReviewSoft')
        else:
                return redirect('ProcessFiles')

def flagsentences(document, restrictions):
                sent_array = []
                strongtext = str("<p>" + document.fulldoctext + "</p>")
                for restriction in restrictions:
                        restrictionsentences = flaggedSentence.objects.filter(restriction=restriction.id)
                        for sentence in restrictionsentences:
                                sentence = str(sentence)
                                if sentence in sent_array:
                                        pass
                                else:
                                        sent_array.append(sentence)
                                        strongtext = str(strongtext.replace(sentence, StrongText(sentence,restriction.flaggedcolor)))
                strongtext = strongtext.replace("\n\n","</p>\n\n<p>")
                return strongtext

def soft_review(request):
        review_docs = processingData.objects.all()
        if review_docs:
                document = processingData.objects.order_by('id').first()
                softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                restrictions = restrictionTitle.objects.all()                
                flaggedrestrictions = flaggedRestriction.objects.filter(filename=document.id)
                strongtext = flagsentences(document, flaggedrestrictions)
                return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions, 'FlaggedRestrictions':flaggedrestrictions, 'Strongtext':strongtext})
        else:
                return redirect('Home')

def next_review(request,pk):
        review_docs = processingData.objects.all()
        if request.method == 'POST':
                document = processingData.objects.get(id=pk)
                if processingData.objects.filter(id__gte=document.id).exclude(id=document.id).order_by('id').first():
                        document = processingData.objects.filter(id__gte=document.id).exclude(id=document.id).order_by('id').first()
                softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                restrictions = restrictionTitle.objects.all()
                flaggedrestrictions = flaggedRestriction.objects.filter(filename=document.id)
                strongtext = flagsentences(document, flaggedrestrictions)
                return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions, 'FlaggedRestrictions':flaggedrestrictions, 'Strongtext':strongtext})
                

def prev_review(request,pk):
        review_docs = processingData.objects.all()
        if request.method == 'POST':
                document = processingData.objects.get(id=pk)
                if processingData.objects.filter(id__lte=document.id).exclude(id=document.id).order_by('-id').first():
                        document = processingData.objects.filter(id__lte=document.id).exclude(id=document.id).order_by('-id').first()
                softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                restrictions = restrictionTitle.objects.all()
                flaggedrestrictions = flaggedRestriction.objects.filter(filename=document.id)
                strongtext = flagsentences(document, flaggedrestrictions)
                return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions, 'FlaggedRestrictions':flaggedrestrictions, 'Strongtext':strongtext})

def del_review(request,pk):
        if request.method == 'POST':
                currentrecord = processingData.objects.get(pk=pk)
                currentrecord.delete()
                return redirect('ReviewSoft')

def update_review(request,pk):
        document = processingData.objects.get(id=pk)
        if request.method == 'POST':
                restrictionarray = []
                i = 0
                for item in request.POST:
                        if i < 4:
                                pass
                        else:
                                restrictionarray.append(request.POST.get(item))
                        i += 1

                softwareIndex.objects.create(softwarename=request.POST.get('Softwarename'),publishername=request.POST.get('Publishername'),informationurl=request.POST.get('Informationpage'), flaggedrestrictions=ArrayToString(restrictionarray))                
                document.delete()
                return redirect('Software')
                

def Software(request):
        all_software = softwareIndex.objects.all()
        review_docs = processingData.objects.all()
        return render(request,"software.html",{'PendingReview':review_docs,'Softwares': all_software})

def del_software(request, pk):
        if request.method == 'POST':
                softwarerecord = softwareIndex.objects.get(pk=pk)
                softwarerecord.delete()
                return redirect('Software')