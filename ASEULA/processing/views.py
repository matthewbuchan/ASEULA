from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from .models import positiveTerm, negativeTerm, restrictionTitle, restrictionTerm, infoFieldCategory, infoFieldArray, processingData, fileQueue, flaggedRestriction, flaggedSentence, softwareIndex
from .processfile import AseulaMain, ProcessInputFile, ConvertAnsi, ParagraphParse, BulletUpperRemove, ParagraphToLower, UrlList, RemoveNewLine, ProcessRestrictions, ProcessRestrictionType, HighlightText, StrongText, ArrayMode, RemoveDuplicate, ArrayToString, XlsxDump
from django.conf import settings
import datetime, re, os, getpass, subprocess,sys

# Create your views here.
def Home(request):
        all_documents = fileQueue.objects.all()
        review_docs = processingData.objects.filter(reviewed=False)
        return render(request, 'main.html', {'Documents' : all_documents, 'PendingReview':review_docs})
def ImportFile(request):
        review_docs = processingData.objects.filter(reviewed=False)
        filequeue = fileQueue.objects.all()
        if request.method == "POST":
                if request.FILES:
                        filelist = request.FILES
                        filelisting = request.FILES.getlist('document')
                        postfile = filelist['document']
                        if len(filelisting) >= 2:
                                for items in filelisting:
                                        fs=FileSystemStorage()
                                        queuename = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
                                        fs.save("processing/"+ str(queuename) + str(items), items)
                                        fileQueue.objects.create(filefield="processing/"+ str(queuename) + str(items), filename=str(queuename) + str(items))
                        else:
                                fs=FileSystemStorage()
                                fs.save("processing/"+ str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(postfile),postfile)
                                fileQueue.objects.create(filefield="processing/"+ str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + str(filelist['document']), filename=str(datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(request.FILES)))
                        return redirect('Home')
                else:
                        pass
        return render(request, 'importfile.html', {'PendingReview':review_docs,'FileQueue':filequeue,})
def ImportText(request):
        review_docs = processingData.objects.filter(reviewed=False)
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
        review_docs = processingData.objects.filter(reviewed=False)
        softwarelist = softwareIndex.objects.all()
        if review_docs:
                document = processingData.objects.filter(reviewed=False).order_by('id').first()
                softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                restrictions = restrictionTitle.objects.all()
                flaggedrestrictions = flaggedRestriction.objects.filter(filename=document.id)
                strongtext = flagsentences(document, flaggedrestrictions)
                return render(request, 'revdocs.html', {'Softwares': softwarelist,'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions, 'FlaggedRestrictions':flaggedrestrictions, 'Strongtext':strongtext})
        else:
                return redirect('Home')
def next_review(request,pk):
        review_docs = processingData.objects.filter(reviewed=False)
        if request.method == 'POST':
                document = processingData.objects.get(id=pk)
                if processingData.objects.filter(reviewed=False,id__gte=document.id).exclude(id=document.id).order_by('id').first():
                        document = processingData.objects.filter(reviewed=False,id__gte=document.id).exclude(id=document.id).order_by('id').first()
                softwarefield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="software name").id)
                publisherfield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="publisher").id)
                infofield = infoFieldArray.objects.filter(filename=document.id, categoryname=infoFieldCategory.objects.get(categoryname="information webpage").id)
                restrictions = restrictionTitle.objects.all()
                flaggedrestrictions = flaggedRestriction.objects.filter(filename=document.id)
                strongtext = flagsentences(document, flaggedrestrictions)
                return render(request, 'revdocs.html', {'PendingReview':review_docs,'RevDoc':document,'InfoField':infofield,'SoftwareField':softwarefield,'PublisherField':publisherfield, 'Restrictions':restrictions, 'FlaggedRestrictions':flaggedrestrictions, 'Strongtext':strongtext})
def prev_review(request,pk):
        review_docs = processingData.objects.filter(reviewed=False)
        if request.method == 'POST':
                document = processingData.objects.get(id=pk)
                if processingData.objects.filter(reviewed=False,id__lte=document.id).exclude(id=document.id).order_by('-id').first():
                        document = processingData.objects.filter(reviewed=False,id__lte=document.id).exclude(id=document.id).order_by('-id').first()
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
def submit_review(request,pk):
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
                if softwareIndex.objects.filter(softwarename=request.POST.get('Softwarename')) :
                        #Update software information in software list
                        softwareIndex.objects.filter(softwarename=request.POST.get('Softwarename')).update(softwarename=request.POST.get('Softwarename'),publishername=request.POST.get('Publishername'),informationurl=request.POST.get('Informationpage'), flaggedrestrictions=re.sub(', ',';#',ArrayToString(restrictionarray)),checkdate=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) ,checkby=str(getpass.getuser()))
                else:
                        #Create new record in software list
                        softwareIndex.objects.create(softwarename=request.POST.get('Softwarename'),publishername=request.POST.get('Publishername'),informationurl=request.POST.get('Informationpage'), flaggedrestrictions=re.sub(', ',';#',ArrayToString(restrictionarray)),checkdate=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) ,checkby=str(getpass.getuser()))
                processingData.objects.filter(pk=pk).update(parentsoftware=softwareIndex.objects.get(softwarename=request.POST.get('Softwarename')),reviewed=True)
                for record in processingData.objects.filter(parentsoftware=softwareIndex.objects.get(softwarename=request.POST.get('Softwarename'))).exclude(id=document.id):
                        record.delete()
                return redirect('ReviewSoft')
def Software(request):
        all_software = softwareIndex.objects.all().order_by('softwarename')
        review_docs = processingData.objects.filter(reviewed=False)
        return render(request,"software.html",{'PendingReview':review_docs,'Softwares': all_software})
def del_software(request, pk):
        if request.method == 'POST':
                softwarerecord = softwareIndex.objects.get(pk=pk)
                softwarerecord.delete()
                return redirect('Software')
# Individual Software change screen
def change_soft(request,pk):        
        softwarelist = softwareIndex.objects.all()
        review_docs = processingData.objects.all()
        if review_docs:
                document = processingData.objects.filter(parentsoftware=pk).first()
                softdoc = softwareIndex.objects.get(pk=pk)
                # softwarefield = softwareIndex.objects.get(pk=pk).softwarename
                # publisherfield = softwareIndex.objects.get(pk=pk).publishername
                # infofield = softwareIndex.objects.get(pk=pk).informationurl
                restrictions = restrictionTitle.objects.all()
                flaggedrestrictions = flaggedRestriction.objects.filter(filename=document.id)
                selectedrestrictions = softwareIndex.objects.get(pk=pk).flaggedrestrictions.split(';#')
                strongtext = flagsentences(document, flaggedrestrictions)
                return render(request, 'updatesoft.html', {'Softwares': softwarelist,'PendingReview':review_docs,'RevDoc':document,'SoftDoc':softdoc, 'Restrictions':restrictions, 'FlaggedRestrictions':flaggedrestrictions, 'SelectedRestrictions':selectedrestrictions, 'Strongtext':strongtext})
        else:
                return redirect('Software')
# Individual Software update command
def submit_soft(request,pk):
        document = softwareIndex.objects.get(pk=pk)
        if request.method == 'POST':
                restrictionarray = []
                i = 0
                for item in request.POST:
                        if i < 4:
                                pass
                        else:
                                restrictionarray.append(request.POST.get(item))
                        i += 1
                if softwareIndex.objects.filter(softwarename=request.POST.get('Softwarename')):
                        #Update software information in software list
                        print("updating software:",request.POST.get('Softwarename'))
                        print(document.checkdate)
                        softwareIndex.objects.filter(softwarename=request.POST.get('Softwarename')).update(softwarename=request.POST.get('Softwarename'),publishername=request.POST.get('Publishername'),informationurl=request.POST.get('Informationpage'), flaggedrestrictions=re.sub(', ',';#',ArrayToString(restrictionarray)),checkdate=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) ,checkby=str(getpass.getuser()))
                else:
                        #Create new record in software list
                        softwareIndex.objects.create(softwarename=request.POST.get('Softwarename'),publishername=request.POST.get('Publishername'),informationurl=request.POST.get('Informationpage'), flaggedrestrictions=re.sub(', ',';#',ArrayToString(restrictionarray)),checkdate=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),checkby=str(getpass.getuser()))
                processingData.objects.filter(pk=pk).update(parentsoftware=softwareIndex.objects.get(softwarename=request.POST.get('Softwarename')),reviewed=True)
                # for record in processingData.objects.filter(parentsoftware=softwareIndex.objects.get(softwarename=request.POST.get('Softwarename'))).exclude(id=document.id):
                #         record.delete()
                return redirect('Software')                
def export_file(request):
        import subprocess #allows execution of powershell commands
        export_docs = softwareIndex.objects.all()
        export_date = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))        
        if request.method == 'POST':
                job_array = []
                for record in export_docs:
                        record_elements = []
                        record_elements.append(record.softwarename)
                        record_elements.append(record.publishername)
                        record_elements.append(record.informationurl)
                        record_elements.append(record.flaggedrestrictions)
                        job_array.append(record_elements)
                XlsxDump(job_array, export_date)
                os.system('powershell.exe -ExecutionPolicy Bypass ..\export_to_sharepoint.ps1')
                purgelist = softwareIndex.objects.all()
                for item in purgelist:
                        item.delete()
                return redirect('pushsuccess')
def pushsuccess(request):
        all_documents = fileQueue.objects.all()
        review_docs = processingData.objects.filter(reviewed=False)
        return render(request, 'pushsuccess.html', {'Documents' : all_documents, 'PendingReview':review_docs})