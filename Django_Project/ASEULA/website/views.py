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
        return render(request, 'main.html', {'Documents' : all_documents})

def ImportFile(request):
        form = UploadFileForm()        
        if request.method == "POST":                
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                        form.save()
                        return redirect('Home')
        else:
                form = UploadFileForm()
        return render(request, 'importfile.html', {
                'form': form})

def ImportText(request):
        if request.method == 'POST':
                usertext = request.POST.get('document')
                print(usertext)
                tempfile = str("usertxt" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
                f = open(tempfile+".txt",mode="w+")
                f.write(str(usertext))
                f.close()
                form = UploadFileForm()
                form = UploadFileForm(request.POST, tempfile + ".txt")
                if form.is_valid():
                        form.save()
                        return redirect('Home')
        return render(request, 'importtext.html')

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
                                # f = fileQueue.objects.get(pk=filename.pk)
                                # f.delete()
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

                                # print(jobData[4],"\n\n") => information summary lists dictionary
                                # for key in jobData[5]:
                                #         print(key)
                                #         print(jobData[5][key],"\n\n") => flagged sentences dictionary
                                # print(jobData[6],"\n\n") => complete document text
                documents = processingData.objects.all()
                return render(request, 'docreview.html', {'RevDocs':documents,})
        else:
                return render(request,"loading.html", {'file_list':file_list,})

def ReviewSoft(request):
        documents = processingData.objects.all()
        return render(request, 'docreview.html', {'RevDocs':documents,})


def Software(request):
        all_software = softwareIndex.objects.all()
        return render(request,"software.html",{'Softwares': all_software})