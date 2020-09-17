from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from processing.models import positiveTerm, negativeTerm, restrictionTitle, restrictionTerm,infoFieldCategory,infoFieldArray,processingData,fileQueue, flaggedRestriction, flaggedSentence
from processing.processfile import *
from django.conf import settings
from .models import softwareIndex
from .forms import UploadFileForm
import datetime

# Create your views here.
def Home(request):
        all_documents = fileQueue.objects.all()
        review_docs = processingData.objects.all()
        return render(request, 'main.html', {'Documents' : all_documents, 'PendingReview':review_docs})

def ImportFile(request):
        review_docs = processingData.objects.all()
        filequeue = fileQueue.objects.all()
        form = UploadFileForm()
        if request.method == "POST":
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                        form.save()
                        return redirect('Home')
        else:
                form = UploadFileForm()
        return render(request, 'importfile.html', {'PendingReview':review_docs,'form': form,'FileQueue':filequeue,})

def ImportText(request):
        review_docs = processingData.objects.all()
        filequeue = fileQueue.objects.all()
        if request.method == 'POST':
                usertext = request.POST.get('document')
                tempfile = str("usertxt" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+ ".txt")                
                f = open(tempfile,mode="w+")
                f.write(str(usertext))                
                fs = FileSystemStorage()
                fs.save("processing/"+ str(f.name),f)
                fileQueue.objects.create(filefield="processing/"+ str(f.name), filename=f.name)
                f.close()
                return redirect('Home')
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
                                for category in jobData[5]:
                                        if flaggedRestriction.objects.filter(restriction__icontains=category.lower()):
                                                pass
                                        else:
                                                flaggedRestriction.objects.create(filename=processingData.objects.get(filename=jobData[0]),restriction=category)
                                        for sentence in jobData[5][category]:
                                                flaggedSentence.objects.create(filename=processingData.objects.get(filename=jobData[0]), restriction=flaggedRestriction.objects.get(restriction=category), sentence=sentence)
                document = processingData.objects.order_by('id').first()
                return render(request, 'revdocs.html', {'RevDoc':document, 'PendingReview': document})
        else:
                return render(request,"main.html", {'file_list':file_list,})

def soft_review(request):
        review_docs = processingData.objects.all()
        if review_docs:
                document = processingData.objects.order_by('id').first()
                softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                restrictions = flaggedRestriction.objects.filter(filename=document.id)
                return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions})
        else:
                return redirect('Home')

def next_review(request,pk):
        review_docs = processingData.objects.all()
        if request.method == 'POST':
                document = processingData.objects.get(id=pk)
                next_document = processingData.objects.filter(id__gte=document.id).exclude(id=document.id).order_by('id').first()                
                if next_document == None:
                        softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                        publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                        infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                        restrictions = flaggedRestriction.objects.filter(filename=document.id)
                        return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions})
                else:                        
                        softwarefield = infoFieldArray.objects.filter(filename=next_document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                        publisherfield = infoFieldArray.objects.filter(filename=next_document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                        infofield = infoFieldArray.objects.filter(filename=next_document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                        restrictions = flaggedRestriction.objects.filter(filename=next_document.id)
                        return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':next_document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions})

def prev_review(request,pk):
        review_docs = processingData.objects.all()
        if request.method == 'POST':
                document = processingData.objects.get(id=pk)                
                prev_document = processingData.objects.filter(id__lte=document.id).exclude(id=document.id).order_by('-id').first()                
                if prev_document == None:                        
                        softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                        publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                        infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                        restrictions = flaggedRestriction.objects.filter(filename=document.id)
                        return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions})
                else:                        
                        softwarefield = infoFieldArray.objects.filter(filename=prev_document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                        publisherfield = infoFieldArray.objects.filter(filename=prev_document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                        infofield = infoFieldArray.objects.filter(filename=prev_document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                        restrictions = flaggedRestriction.objects.filter(filename=prev_document.id)
                        return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':prev_document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions})

def del_review(request,pk):
        if request.method == 'POST':
                currentrecord = processingData.objects.get(pk=pk)
                currentrecord.delete()
                return redirect('ReviewSoft')

def update_review(request,pk):
        document = processingData.objects.get(id=pk)
        review_docs = processingData.objects.all()
        if request.method == 'POST':
                document.softwarename = request.POST.get('Softwarename')
                document.publishername = request.POST.get('Publishername')
                document.informationpage = request.POST.get('Informationpage')
                document.save()
                restrictions = flaggedRestriction.objects.filter(filename=document.id)
                print(request.POST.get('Informationpage'))
                return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document, 'Restrictions':restrictions})

                

def Software(request):
        all_software = softwareIndex.objects.all()
        review_docs = processingData.objects.all()
        return render(request,"software.html",{'PendingReview':review_docs,'Softwares': all_software})