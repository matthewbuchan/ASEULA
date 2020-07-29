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
import os.path
from spacy.lang.en import English
from re import search
from statistics import mode
from wand.image import Image as wi
from tqdm import tqdm
from pathlib import Path
from PIL import Image as im
# from sense2vec import Sense2Vec #Sense2Vec installation required with s2v_md files for the FindSimilarTerms function
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
nlp = spacy.load('en_core_web_sm') # Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
###############################################    FUNCTIONS    ###############################################
def ProcessInputFile(inputfilename): # Determines file type and conversion steps
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
def ConvertAnsi(file_input): # Converts .txt files if not formatted properly (UTF-8 > ANSI)
    import codecs
    inputfile = file_input
    if current_sys.lower() == "windows":
        with io.open( inputfile , mode='r', encoding='utf8') as fc:
            content = fc.read()
        return content
    else:
        return inputfile
def paragraph_parse(ocr_input): # Splits paragraphs before processing text
    all_paragraphs = re.split('\n{2,}', ocr_input)
    parsed_paragraphs = ""
    for paragraph in all_paragraphs:
        paragraph = paragraph.replace("\n", " ")
        parsed_paragraphs += str(paragraph) + "\n"
    return parsed_paragraphs
def UrlList(sentences): # Generates listing of websites identified in the document
    from spacy import attrs
    UrlList = []    
    for sentence in sentences:
        doc = nlp(str(sentence))
        for token in doc:
            if token.like_url == True:
                UrlList.append(token.text)
    return UrlList
def AseulaMain(document,full_job_text): # Performs data extraction from the converted documents
    #**********************************************    Organization     ***************************************************#
    # Establish variables to store publisher
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
    
    restriction_sentence_dict,rxion_array = ProcessRestrictions(document)
    rxion_array_string = ArrayToString(RemoveDuplicate(rxion_array))

    fields = ["Software name", "Publisher","Information Webpage",  "Licensing Restrictions"]
    selected_variables_dict = {"software name": software_name, "publisher": publisher_name, "information webpage": information_webpage, "licensing restrictions": rxion_array_string}
    field_variables_dict = {"software name": software_findings, "publisher": RemoveDuplicate(organization_entity_array), "information webpage": RemoveDuplicate(url_array)}
    
    return [os.path.basename(job),selected_variables_dict,fields,rxion_array,field_variables_dict,restriction_sentence_dict,full_job_text]
def ProcessRestrictions(document): # Establishes restriction variables and executes each type
    rxion_array = []
    rxion_patterns = {}
    pos_trigger_words = ["only", "grant", "grants", "granting", "granted", "allow", "allows", "allowing", "allowed", "permit", \
        "permits", "permitting", "permitted", "require", "requires", "requiring", "required", "authorize", "authorizes", \
            "authorizing", "authorized", "necessary"]
    neg_trigger_words = ["no", "not", "may not", "not granted", "not allowed", "not permitted", "forbidden", "restricts", "restricted",\
         "prohibits", "prohibited"]
    rxion_patterns["Instructional-use only"] = ["teaching", "teaching use", "teaching-use", "instruction", "instructional use",\
         "instructional-use", "instructional purposes", "academic", "academic use", "academic-use", "academic instruction",\
              "academic institution", "academic purposes", "educational", "educational use", "educational-use",\
                   "educational instruction", "educational institution", "institution", "educational purposes"]
    rxion_patterns["Research-use only"] = ["research", "research use", "research-use"]
    rxion_patterns["Requires Physical Device"] = ["activation key", "dongle"]
    rxion_patterns["No RDP use"] = ["remote", "rdp", "remote access", "remote-access", "remote desktop", "remote interface"]
    rxion_patterns["Use geographically limited (Campus)"] = ["designated site", "customer's campus", "internally"]
    rxion_patterns["Use geographically limited (radius)"] = ["radius", "limited radius", "geographically limited radius",\
         "geographically-limited radius", "particular geography", "site license", "site licenses"]
    rxion_patterns["US use only"] = ["united states", "united states use", "u.s.", "u.s. use","export"]
    rxion_patterns["VPN required off-site"] = ["vpn", "virtual private network", "remote access"]
    rxion_patterns["Block embargoed countries"] = ["embargo", "embargoed", "embargoed country","export"]
    rxion_patterns["Block use from Persons of Concern"] = ["person of concern", "persons of concern", "people of concern",\
        "denied persons"]
    rxion_patterns["On-site (lab) use only"] = ["lab-use"]
    rxion_patterns["On-site use for on-site students only"] = ["single fixed geographic site", "fixed geographic site",\
         "geographic site", "on-site", "on-site use"]
    rxion_patterns["Virtualization Allowed"] = ["virtualization", "virtualizing", "multiplexing", "pooling"]
    restriction_sentence_dict = dict()

    # Restriction runs
    for rxion in rxion_patterns:
        rxiontmp = ProcessRestrictionType(document,rxion_patterns[str(rxion)],pos_trigger_words,neg_trigger_words,str(rxion))
        if rxiontmp:
            rxion_array.append(str(rxion))
            restriction_sentence_dict[str(rxion)] = RemoveDuplicate(rxiontmp)
    if not rxion_array:
        rxion_array.append("Needs Review")
    return restriction_sentence_dict, rxion_array    
def ProcessRestrictionType(document,restrictions,pos,neg,restrictionString): # Function to find restriction sentences
    rxion_sentences_array = []
    rx_array = [(p,n,r) for p in pos for n in neg for r in restrictions]
    for sent in document.sents:
        sentence = str(sent).lower()
        for rx in rx_array:
            if rx[2] in sentence: # All sentences containing a restriction
                if any(pattern in restrictionString.lower() for pattern in neg): # All sentences containing a negative trigger
                    if rx[0] in sentence and str(sent) not in rxion_sentences_array and HighlightText(str(sent)) not in rxion_sentences_array:
                        reg_pattern = re.compile(rx[1] + r"(.*" + rx[0] + r")?.*" + rx[2])
                        reg_pattern_rev = re.compile(rx[2] + r".*" + rx[1] + r"(.*" + rx[0] + r")?")
                        if re.search(reg_pattern,sentence):
                            rxion_sentences_array.append(HighlightText(str(sent)))
                        elif re.search(reg_pattern_rev,sentence):
                            rxion_sentences_array.append(HighlightText(str(sent)))
                    elif rx[0] not in sentence and str(sent) not in rxion_sentences_array and HighlightText(str(sent)) not in rxion_sentences_array:
                        reg_pattern = re.compile(rx[1] + r"(.*" + rx[0] + r")?.*" + rx[2])
                        reg_pattern_rev = re.compile(rx[2] + r".*" + rx[1] + r"(.*" + rx[0] + r")?")
                        if re.search(reg_pattern,sentence):
                            rxion_sentences_array.append(HighlightText(str(sent)))
                        elif re.search(reg_pattern_rev,sentence):
                            rxion_sentences_array.append(HighlightText(str(sent)))
                elif rx[0] in sentence and str(sent) not in rxion_sentences_array and HighlightText(str(sent)) not in rxion_sentences_array: # All sentences containing a positive trigger
                    reg_pattern = re.compile(r"("+ rx[1] + r".*)?" + rx[0] + r".*" + rx[2])
                    reg_pattern_rev = re.compile(rx[2] + r"(.*" + rx[1] + r".*)?" + rx[0])
                    if re.search(reg_pattern,sentence):
                        rxion_sentences_array.append(HighlightText(str(sent)))
                    elif re.search(reg_pattern_rev,sentence):
                        rxion_sentences_array.append(HighlightText(str(sent)))
                elif str(sent) not in rxion_sentences_array and HighlightText(str(sent)) not in rxion_sentences_array:
                    rxion_sentences_array.append(str(sent))
    if len(rxion_sentences_array) > 0:        
        return rxion_sentences_array
def OutputResults(job): # Summarized output
    print("\nHere's what we found for", job[0])
    print("-----------------------")    
    print("Software: ", job[1]['software name'])
    print("Publisher: ", job[1]['publisher'])
    print("Information Webpage: ", job[1]['information webpage'])
    print("Licensing Restrictions: ", job[1]['licensing restrictions'])
    print("-----------------------")
    UserValidation()
def UserValidation(): # Provides interface for users to validate findings
    while True:
        info_check = str(input("Is the information above correct? (y/n)  ")).lower().strip()
        if info_check == "y":
            print ("Information will shortly pushed to SharePoint. Thank you for using ASEULA!")
            break
        elif info_check == "n":
            for selection in job[2]:
                print(job[2].index(selection) + 1,". ",selection)
            while True:
                field_correction = int(input("\nWe're sorry. Which of the following fields is incorrect? Please enter the corresponding number. "))
                if field_correction == 4:
                    new_rxion_array = RestrictionSentenceOutput(job[5])
                    job[1][job[2][field_correction - 1].lower()] = ArrayToString(RemoveDuplicate(new_rxion_array))
                    print("\n")
                    OutputResults(job)
                    break
                elif field_correction == 1 or field_correction == 2 or field_correction == 3:
                    print ('-' * 10)
                    incorrect_data = job[4][job[2][field_correction - 1].lower()]
                    if incorrect_data:
                        for item in incorrect_data:
                            print(incorrect_data.index(item) + 1,". ",item)
                        while True:
                            user_selection = input("\nWhich value is correct? If none are correct, please enter one. ")
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
                        user_selection = str(input("\nNo value were found, please provide the correct value if it is known. "))
                        if user_selection:
                            job[4][job[2][field_correction - 1].lower()].append(user_selection)
                            job[1][job[2][field_correction - 1].lower()] = user_selection
                        OutputResults(job)
                        break
                else: 
                    print("Error! Invalid input. Please enter a valid field option.")
            break
        else:
            print('Invalid input. Please try again.')
def RestrictionSentenceOutput(dictionary): # Displays restriction sentences used in the UserValidation function
    new_rxion_array = []    
    for key in dictionary:        
        i = 1
        print("-"*25+"\n",key,"\n"+"-"*25+"\n")
        for item in dictionary[key]:
            print(str(i) + ".",item.strip("\n"))
            i += 1
        user_selection = input("\nIs this restriction flagged correctly? (y/n)").lower().strip()
        if user_selection == "y":
            new_rxion_array.append(key)
        elif user_selection == "n":
            print ("This restriction will be unflagged\n")
    return new_rxion_array
def HighlightText(usertext): # Returns inputted text as yellow for easy identification
    return Fore.YELLOW + str(usertext) + Fore.RESET
def ArrayMode(list): # Assists in determining entities from the AseulaMain
    return(mode(list))
def RemoveDuplicate(array): # Removes duplicate elements in an array.
    array = list(dict.fromkeys(array))
    return array
def ArrayToString(array): # Converts an array to a string.
    array_string = ""
    i = 0
    while i <= (len(array)-1):
        if (i != (len(array)-1)):
            array_string += array[i] + ", "
        elif (i == (len(array)-1)):
            array_string += array[i]
        i += 1
    return array_string
def ParagraphToLower(m): # Changes full uppercase paragraphs to lower.
    return m.group(0).lower()
def SimilarityList(sentences, restrictions): #Searches through all tokens to check similarity with restriction items. (Inactive)
    sent_count = 1
    for sentence in sentences:
        doc = nlp(str(sentence))
        rxsion = nlp(restrictions)
        rx_sim = 0
        for token in doc:
            for rx in rxsion:
                if rx.similarity(token) > .70:
                    #print(f'{token.text:{15}}{rx.text:{15}}{rx.similarity(token) * 100}')
                    rx_sim = 1                    
        if rx_sim == 1:            
            print(str(sent_count) + ". " + str(sentence))
            sent_count += 1
# def FindSimilarTerms(inputarray): #Find similar terms for an input variable
#     output_array = []    
#     for element in inputarray:
#         try:
#             output_array.append(element)
#             element = element.replace(" ","_")            
#             s2v = Sense2Vec().from_disk("../../../s2v_reddit_2015_md")
#             query = str(element) + "|NOUN"
#             assert query in s2v
#             vector = s2v[query]
#             freq = s2v.get_freq(query)
#             most_similar = s2v.most_similar(query, n=5)
#             for i in most_similar:            
#                 i = i[0].split("|")
#                 i = i[0].replace("_"," ").lower()
#                 output_array.append(i)                
#         except:
#             pass
#     if output_array > inputarray:
#         return output_array
#     else:
#         return inputarray
#     pass
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
    print("\nASEULA Alpha Build 200727 for",current_sys)
    fileInput = True
    current_sys = platform.system()
    while fileInput == True:        
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
                    if os.path.isdir(inputFile):
                        filelist = os.listdir(inputFile)
                        for line in filelist:    
                            filename_array.append(str(inputFile) + line)
                        print(filename_array)
                        break
                    elif os.path.isfile(inputFile):
                        filename_array.append(inputFile)
                        break
                    else:
                        print(inputFile,"You did not enter a valid file or directory. Read the directions. ")
                        break
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
        jobDataArray.append(AseulaMain(document, full_job_text))
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