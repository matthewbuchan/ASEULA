#############################################    INSTALL/IMPORT    ###########################################
# pip install wheel
# pip install spacy
# python -m spacy download en_core_web_sm
# pip install pytesseract
# pip install wand
# pip install docx2txt
# pip install PyPDF2
# pip install tqdm
# install imagemagick for windows
# install ghostscript for windows
# install Tesseract-OCR for windows

from colorama import Fore, Back, Style
import io, os, sys, re, timeit, statistics, docx2txt, PyPDF2, re, spacy, pytesseract as tess, platform
from spacy.lang.en import English
from spacy.matcher import Matcher
from re import search
from statistics import mode
from wand.image import Image as wi
from tqdm import tqdm
from pathlib import Path
from PIL import Image as im
##############################################    SCRIPT CONFIG    ############################################
current_sys = platform.system()
if current_sys.lower() == "windows":
    if os.path.isfile(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' #WINDOWS DEFAULT INSTALL
    elif os.path.isfile(r'%USERPROFILE%\AppData\Local\Tesseract-OCR\tesseract.exe'):
        tess.pytesseract.tesseract_cmd = r'%USERPROFILE%\AppData\Local\Tesseract-OCR\tesseract.exe' #WINDOWS USER INSTALL
    else:
        tess.pytesseract.tesseract_cmd = input("Please enter the tesseract.exe file path: ")
elif current_sys.lower() == "linux":
    tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' #LINUX

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

# # Establishes variable for English sentence parsing method.
# sentence_parser = English()
# sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))
###############################################    FUNCTIONS    ###############################################
def ProcessInputFile(inputfilename):
    if inputfilename.endswith('.txt'):
        # Opens the .txt file.
        try:
            open_file = open(inputfilename).read()
        except:
            open_file = ConvertAnsi(inputfilename)
        return open_file
    elif inputfilename.endswith('.docx'):
        open_file = docx2txt.process(inputfilename)
        return open_file
    elif inputfilename.endswith('.pdf'):
        pdf = wi(filename = inputfilename, resolution = 300)
        pdfImg = pdf.convert('jpeg')
        open_file = ""
        for img in tqdm(pdfImg.sequence, desc=os.path.basename(inputfilename)):
            page = wi(image = img)
            pic = im.open(io.BytesIO(page.make_blob('jpeg')))
            text = tess.image_to_string(pic, lang = 'eng')
            open_file += text            
        return open_file
    else:
        print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")
def ConvertAnsi(file_input):
    import codecs    
    inputfile = file_input    
    if current_sys.lower() == "windows":
        with io.open( inputfile , mode='r', encoding='utf8') as fc:
            content = fc.read()            
        return content
    else:
        return inputfile
def paragraph_parse(ocr_input):
    all_paragraphs = re.split('\n{2,}', ocr_input)
    parsed_paragraphs = ""
    for paragraph in all_paragraphs:
        paragraph = paragraph.replace("\n", " ")
        parsed_paragraphs += str(paragraph) + "\n"
    return parsed_paragraphs
def UrlList(sentences):
    from spacy import attrs
    UrlList = []    
    for sentence in sentences:
        doc = nlp(str(sentence))
        for token in doc:
            if token.like_url == True:
                UrlList.append(token.text)
    return UrlList
def AseulaFunction(document,full_job_text):
    #**********************************************    Organization     ***************************************************#
    # Establish variables to store publisher
    nlp = spacy.load('en_core_web_sm')
    organization_entity_array = []
    publisher_patterns = ["inc", "inc.","llc","incorporated", "©", "copyright"]
    for entity in document.ents:        
        if entity.label_ == "ORG":
            if any(pattern in entity.text.lower() for pattern in publisher_patterns):
                for element in publisher_patterns:
                    if entity.text != element:
                        organization_entity_array.append(str(entity.text).title())
                    
    # Checks if organization_entity_array is empty. Prints mode of the array if elements exist.
    if organization_entity_array:        
        publisher_name = ArrayMode(organization_entity_array)
        publisher_name = publisher_name.replace('\n', ' ')
    else:        
        publisher_name = "Unknown"
    #**********************************************  Software Name   ***************************************************#
    # Establishes variable to store matching entities.
    person_entity_string = ""    
    for entity in document.ents:        
        if entity.label_ == "PERSON":            
            person_entity_string += entity.text + "\n"    
    propn_check = nlp(person_entity_string)

    # Establishes variable to store matching entities.
    propn_token_array = []    
    for token in propn_check:        
        if token.pos_ == "PROPN":            
            propn_token_array.append(token.text)    
    clean_propn_token_array = RemoveDuplicate(propn_token_array)
    matching = [item for item in clean_propn_token_array if item in publisher_name]
    stripped_matching = RemoveDuplicate(matching)

    if matching:
        software_name = ArrayToString(stripped_matching)
    elif not matching:
        software_name = ArrayMode(propn_token_array)
    else:        
        software_name = "Unknown"
    software_findings = clean_propn_token_array + stripped_matching
    software_findings = RemoveDuplicate(software_findings)

    # Extracts each word within the input file as an array. Space characters used as a delimiter.
    url_array = UrlList(sentences) # FORCE URL FUNCTION FILL instead of regex    
    if url_array:        
        information_webpage = ArrayMode(url_array)        
        information_webpage = information_webpage.replace('\n', '')
    else:        
        information_webpage = "Unknown"
        
    # Establishes variables to store restriction patterns and trigger words.
    rxion_array = []
    rxion_patterns = {}
    pos_trigger_words = ["only","grant","allow","permit","require","authorize"]
    neg_trigger_words = ["not","no","forbid", "restrict", "prohibit"]
    rxion_patterns["Instructional-use only"] = ["teaching", "teach","use", "instructional","academic","institution", "educational"]
    rxion_patterns["Research-use only"] = ["research", "research use", "research-use"]
    rxion_patterns["Requires Physical Device"] = ["activation key"]
    rxion_patterns["No RDP use"] = ["remote access", "remote-access", "remote desktop", "remote interface"]
    rxion_patterns["Use geographically limited (Campus)"] = ["internally","designated site", "customer's campus"]
    rxion_patterns["Use geographically limited (radius)"] = ["radius", "limited radius", "geographically limited radius", "geographically-limited radius", "particular geography", "site license", "site licenses"]
    rxion_patterns["US use only"] = ["united states","united states use", "u.s.", "u.s. use"]
    rxion_patterns["VPN required off-site"] = ["vpn", "virtual private network"]
    rxion_patterns["Block embargoed countries"] = ["embargo", "embargoed", "embargoed country","export"]
    rxion_patterns["Block use from Persons of Concern"] = ["person of concern", "persons of concern", "people of concern","denied persons"]
    rxion_patterns["On-site (lab) use only"] = ["lab-use"]
    rxion_patterns["On-site use for on-site students only"] = ["single fixed geographic site", "fixed geographic site", "geographic site", "on-site", "on-site use"]
    rxion_patterns["Virtualization Allowed"] = ["virtualization", "virtualizing", "multiplexing", "pooling"]
    restriction_sentence_dict = dict()
    
    # Restriction runs
    nlp = spacy.load('en_core_web_sm', disable=["ner"])
    for rxion in rxion_patterns:
        print(str(rxion))
        rxiontmp = ProcessRestrictionType(document,rxion_patterns[str(rxion)],pos_trigger_words,neg_trigger_words,str(rxion))
        if rxiontmp:
            rxion_array.append(str(rxion))
            restriction_sentence_dict[str(rxion)] = rxiontmp

    if not rxion_array:
        rxion_array.append("Needs Review")

    rxion_array_string = ArrayToString(RemoveDuplicate(rxion_array))

    fields = ["Software name", "Publisher","Information Webpage",  "Licensing Restrictions"]
    selected_variables_dict = {"software name": software_name, "publisher": publisher_name, "information webpage": information_webpage, "licensing restrictions": rxion_array_string}
    field_variables_dict = {"software name": software_findings, "publisher": RemoveDuplicate(organization_entity_array), "information webpage": RemoveDuplicate(url_array)}

    return [os.path.basename(job),selected_variables_dict,fields,rxion_array,field_variables_dict,restriction_sentence_dict,full_job_text]
def ProcessRestrictionType(document,restrictions,pos,neg,restrictionString):
    rxion_sentences_array = []
    rx_array = [(p,n,r) for p in pos for n in neg for r in restrictions]
    for rx in rx_array:
        # Process negative and positive
        pattern_a = [{'LEMMA': str(rx[1])},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LEMMA': str(rx[0])},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LOWER': str(rx[2]).lower()}]
        pattern_b = [{'LOWER': str(rx[2]).lower()},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LEMMA': str(rx[1])},{'LEMMA': str(rx[0])}]
        match = RestrictionMatcher(document,pattern_a,pattern_b)
        if match != None and match not in rxion_sentences_array:
            #print(HighlightText(match))
            #rxion_sentences_array.append(match)
            pass
        # Process negative
        pattern_a = [{'LEMMA': str(rx[1])},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LEMMA': str(rx[0]), 'OP': '?'},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LOWER': str(rx[2]).lower()}]
        pattern_b = [{'LOWER': str(rx[2]).lower()},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LEMMA': str(rx[1])},{'TEXT': {'REGEX': r'\w+'},'OP':'?'},{'LEMMA': str(rx[0]), 'OP': '?'}] 
        match = RestrictionMatcher(document,pattern_a,pattern_b)
        if match != None and match not in rxion_sentences_array:
            #print(HighlightText(match))
            #rxion_sentences_array.append(match)
            pass
        # Process positive/negative and positive
        pattern_a = [{'LEMMA': str(rx[0])},{'TEXT': {'REGEX': r'(\w+\W+)+?'},'OP':'?'},{'LOWER': str(rx[2]).lower()}] 
        pattern_b = [{'LOWER': str(rx[2]).lower()},{'TEXT': {'REGEX': r'(\w+\W+)+?'},'OP':'?'},{'LEMMA': str(rx[0])}] 
        match = RestrictionMatcher(document,pattern_a,pattern_b)
        if match != None and match not in rxion_sentences_array:
            #print(HighlightText(match))
            #rxion_sentences_array.append(match)
            pass
    if len(rxion_sentences_array) > 0:
        return rxion_sentences_array
def RestrictionMatcher(document,pattern_a,pattern_b):
    matcher.add('PATTERN_A',None,pattern_a)
    matcher.add('PATTERN_B',None,pattern_b)
    for sentence in document.sents:
        if matcher(sentence):
            return str(sentence)
def OutputResults(job):
    print("\nHere's what we found for", job[0])
    print("-----------------------")    
    print("Software: ", job[1]['software name'])
    print("Publisher: ", job[1]['publisher'])
    print("Information Webpage: ", job[1]['information webpage'])
    print("Licensing Restrictions: ", job[1]['licensing restrictions'])
    print("-----------------------")    
    UserValidation()
def UserValidation():
    while True:
        info_check = str(input("Is the information above correct? (y/n)  ")).lower().strip()
        if info_check == "y":
            print ("Information will shortly pushed to SharePoint. Thank you for using ASEULA!")
            break
        elif info_check == "n":
            for selection in job[2]:
                print(job[2].index(selection) + 1,". ",selection)
                #print (*job[6], sep= ", ")
            while True:
                field_correction = int(input("\nWhich of the fields information needs to be corrected?  "))
                if field_correction == 4:
                    print ('\n')
                    print ('-' * 10)
                    new_rxion_array = RxionFormatting(job[5])
                    job[1][job[2][field_correction - 1].lower()] = ArrayToString(RemoveDuplicate(new_rxion_array)) #selected_variables_dict[field_correction] = new_rxion_array_string
                    OutputResults(job)
                    break
                elif field_correction == 1 or field_correction == 2 or field_correction == 3:
                    print ('-' * 10)
                    incorrect_data = job[4][job[2][field_correction - 1].lower()]
                    for item in incorrect_data:
                        print(incorrect_data.index(item) + 1,". ",item)
                    while True:
                        user_selection = input("\nwhich value is correct?  ")
                        try:
                            user_selection = int(user_selection)
                            if user_selection <= len(incorrect_data) + 1:
                                job[1][job[2][field_correction - 1].lower()] = incorrect_data[user_selection - 1]
                                break
                            else:
                                print("Error! Invalid input. Please enter a valid number or string.")
                        except:
                            if type(user_selection) == str:
                                job[4][job[2][field_correction - 1].lower()].append(user_selection)
                                job[1][job[2][field_correction - 1].lower()] = user_selection                                
                                break                    
                    OutputResults(job)
                    break
                else: 
                    print("Error! Invalid input. Please enter a valid field option.")
            break
        else:
            print('Invalid input. Please try again.')
def RxionFormatting(dictionary):
    new_rxion_array = []
    for key in dictionary:
        if key in job[3]:
            print (key)
            print("-----------------------")
            # # Added loop to print entire document with flagged text highlighted
            # doctext = str(job[10])
            # for element in dictionary[key]:
            #     doctext = re.sub(str(element),str(HighlightText(element)),doctext)
            # print(doctext)
            ArrayFormatting(dictionary[key])
            user_selection = input("\nIs this restriction flagged correctly? (y/n)  ").lower().strip()
            if user_selection == "y":
                new_rxion_array.append(key)
            elif user_selection == "n":
                print ("This restriction will be unflagged\n")
    return new_rxion_array
def ArrayFormatting(array):
    i=1
    for element in array:
        print (str(i) + ".", element)
        i+=1
    print ("\n")
def HighlightText(usertext):
    return Fore.YELLOW + str(usertext) + Fore.RESET
def ArrayMode(list): # Function that finds the mode of an array.
    return(mode(list))
def RemoveDuplicate(array): # Function that removes duplicate elements in an array.
    array = list(dict.fromkeys(array))
    return array
def ArrayToString(array): # Function that returns array elements as string.
    array_string = ""
    i = 0
    while i <= (len(array)-1):
        if (i != (len(array)-1)):
            array_string += array[i] + ", "
        elif (i == (len(array)-1)):
            array_string += array[i]
        i += 1
    return array_string
def ParagraphToLower(m):
    return m.group(0).lower()
###############################################    EXECUTION    ###############################################
filename_array = [] #Filename storage for jobs
rxion_array = []
rxionjob_sentence_array = [] #Temporary pattern matched sentence storage for jobs
jobDataArray = []
i = 0
if len(sys.argv) >= 2:    
    for filename in sys.argv[1:]:
        fileArray = []
        filename_array.append(filename.strip('"'))
        i += 1
else:
    print("\nASEULA Alpha V.1 for",current_sys)    
    fileInput = True
    current_sys = platform.system()
    while fileInput == True:
        # inputFile = input("\nPlease enter the absolute path for file #" + str(len(filename_array) + 1) + " (or press enter to continue): ").strip('"')
        inputFile = input("\nPlease enter the absolute path for file or directory you would like to process (or press enter to continue): ").strip('"')
        if inputFile != "":
            if current_sys.lower() == "windows":
                while True:
                    if os.path.isdir(inputFile) == True:
                        filelist = os.listdir(inputFile)        
                        for f in filelist:
                            if ".pdf" in str(f) or ".docx" in str(f) or ".txt" in str(f):
                                filename_array.append(str(inputFile) + "\\" + str(f))
                        break
                    elif os.path.isfile(inputFile) == True:
                        filename_array.append(inputFile)
                        break
                    else:
                        print("You did not enter a valid file or directory. Read the directions. ")
            elif current_sys.lower() == "linux":
                while True:
                    if os.path.isdir(inputFile) == True:
                        filelist = os.system("ls -la *.pdf *.txt *.docx | awk '{print \"\\\"\"$9" "$10\"\\\"\"}' > newfile.txt")
                        f_list = ""
                        listfile = open("newfile.txt")
                        for line in listfile:    
                            f_list = f_list +"./"+ line.strip('\"\n') + " "
                        os.system("python3 ../Python/Experiments/Testcoding-regex.py " + f_list)
                        break
                    elif os.path.isfile(inputFile) == True:
                        filename_array.append(inputFile)
                        break
                    else:
                        print("You did not enter a valid file or directory. Read the directions. ")
            else:
                print("Sorry, this script is only compatible with superior operating systems. Get a real computer, jack a**. ")
        else:            
            fileInput = False

if len(filename_array) > 0:
    start = timeit.default_timer()
    print("Please wait while we process",len(filename_array),"file(s)... \n")
    for job in filename_array:
        inputfile = ProcessInputFile(job)
        text = paragraph_parse(inputfile)
        text = re.sub(r'\([A-z0-9]{1,3}?\)',"",text) # Remove (a), (b), (iii) bulleting
        text = re.sub(r'\b[A-Z]{2,}\b',ParagraphToLower,text) #Change full uppercase paragraphs to lower        
        document = nlp(text)
        sentences = []
        for sent in document.sents:
            sentences.append(re.sub(r'\n{1,}'," ",str(sent))) # Remove new line characters from each sentence            
        full_job_text = ""
        for sentence in sentences:
            full_job_text = full_job_text + str(sentence) + "\n"        
        jobDataArray.append(AseulaFunction(document, full_job_text))
        i += 1
    end = timeit.default_timer()
    runtime = end - start
    if runtime > 59:
        print("\n\nFile processing complete. (Processing time: " + str(runtime/60) + " Minutes)\nPlease verify the results: ")
    else:
        print("\n\nFile processing complete. (Processing time: " + str(runtime) + " Seconds)\nPlease verify the results: ")        
    for job in jobDataArray:
            OutputResults(job)
else:
    print("\nNo input was provided. Thank you for using ASEULA!\n")