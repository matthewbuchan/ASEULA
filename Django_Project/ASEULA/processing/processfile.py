####################################################    INSTALLATION STEPS    ###############################################################
#                                                Required programs to run ASEULA-DJANGO                                                     #
#############################################################################################################################################
# pip install wheel
# pip install spacy
# python -m spacy download en_core_web_sm
# pip install pytesseract
# pip install wand
# pip install docx2txt
# pip install openpyxl
# pip install wfastcgi
# wfastcgi-enable
# install imagemagick for windows using default system installation settings
# install ghostscript for windows 
# install Tesseract-OCR for windows 

############################################################    IMPORT    ###################################################################
#                                            Defines all modules required to be imported                                                    #
#############################################################################################################################################

from colorama import Fore, Back, Style
import io, os, sys, re, timeit, statistics, docx2txt, re, spacy, csv, pytesseract as tess, platform, openpyxl
import os.path
from spacy.lang.en import English
from re import search
from statistics import mode
from wand.image import Image as wi
from tqdm import tqdm
from pathlib import Path
from PIL import Image as im
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from .models import * # DJANGO SPECIFIC

###################################################    SYSTEM CONFIGURATION    ##############################################################
#                                            Defines all system configuration variables                                                     #
#############################################################################################################################################

current_sys = platform.system() # Loads current operating system name as a variable
if current_sys.lower() == "windows": # Checks if variable is Windows
    if os.path.isfile(r'C:\Program Files\Tesseract-OCR\tesseract.exe'): # Checks if tesseract installation exists
        tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Tesseract path set for default Windows installation path
        print(">>Tesseract installation located.<<")
    else:
        print(">>Tesseract installation not found.<<")
elif current_sys.lower() == "linux": # Checks if variable is Linux
    if os.path.isfile(r'/usr/bin/tesseract'): # Checks if tesseract installation exists
        tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # Tesseract path set for default Linux installation path
        print(">>Tesseract installation located.<<")
    else:
        print("\n>>Tesseract installation not found. Please install tesseract in the default location<<\n")
nlp = spacy.load('en_core_web_sm') # Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.

#######################################################    SYSTEM FUNCTIONS    ##############################################################
#                                          Defines all system functions executed by DJANGO                                                  #
#############################################################################################################################################

def AseulaMain(jobfile, pos, neg, rxion_dict): # Performs data extraction from the converted documents
    #**********************************************    Organization     ***************************************************#
    processed_file = ProcessInputFile(jobfile) # Determines file type and conversion steps.
    parsed_paragraphs = ParagraphParse(processed_file) # Splits paragraphs before processing text.
    text = BulletUpperRemove(parsed_paragraphs) # Cleans bulleted items in document and converts full uppercase paragraphs to lower.
    document = nlp(text) # Sets document text to a Natural Language Processing (NLP) format.
    sentences = [] # Array initialized to store individual sentences retrieved from NLP processing.
    for sent in document.sents: # Extracts each sentence from NLP document.
        sentences.append(RemoveNewLine(sent)) # Remove new line characters from each sentence and appends to sentence array.
    full_job_text = "" # Sets variable to store full document text
    for sentence in sentences: # Extracts each sentence from the sentence array.
        full_job_text = full_job_text + str(sentence) + "\n" # Concatenates each sentence to the full job text file with a new line character.
    # Establish variables to store publisher
    organization_entity_array = [] # Defines array to store items determined as organizational entities
    publisher_patterns = ["inc", "inc.","llc","incorporated", "©", "copyright"] # Defines patterns to identify publishers
    for entity in document.ents: # For each NLP entity object
        if entity.label_ == "ORG": # If the entity label == ORG
            if any(pattern in entity.text.lower() for pattern in publisher_patterns): # If entity value contains any pattern from publisher_patterns
                for element in publisher_patterns: 
                    if entity.text != element:
                        organization_entity_array.append(str(entity.text).title()) # Append entity value to organization_entity_array
                    
    # Checks if organization_entity_array is empty. Prints mode of the array if elements exist.
    if organization_entity_array: # If organizations are contained in the array
        publisher_name = ArrayMode(organization_entity_array) # Uses mode to select the publisher name
        publisher_name = publisher_name.replace('\n', ' ') # Removes the newline character from the string
    else: # If no organizations are listed in the organization_entity_array
        publisher_name = "Unknown" # Set publisher name to Unknown
    #**********************************************  Software Name   ***************************************************#
    # Establishes variable to store matching entities.
    person_entity_string = "" # Establishes string variable for software name
    for entity in document.ents: # For each NLP entity object
        if entity.label_ == "PERSON": # If entity label = PERSON
            person_entity_string += entity.text + "\n" # Set person_entity_string to entity.text
    propn_check = nlp(person_entity_string) # Stores NLP object as propn_check variable

    # Establishes variable to store matching entities.
    propn_token_array = [] # Defines array to store propn tokens
    for token in propn_check: # Loops through each token in propn_check
        if token.pos_ == "PROPN":  # Verifies the NLP object is a proper noun (common for the entity type)
            propn_token_array.append(token.text) # Appends the token text to the propn_token_array
    clean_propn_token_array = RemoveDuplicate(propn_token_array) # Removes duplicate tokens from propn_token_array
    matching = [item for item in clean_propn_token_array if item in publisher_name] # Finds all items contained in both propn_token_array and person_entity_string
    stripped_matching = RemoveDuplicate(matching) # Removes all duplicate items from matching and stores in stripped_matching
    if matching: # If there are names in matching
        software_name = ArrayToString(stripped_matching) # Sets array to string
    elif not matching: # If there are no names matching
        software_name = ArrayMode(propn_token_array) # Set software_name by using the ArrayMode function
    else: # If no others
        software_name = "Unknown" # Set software name to Unknown
    software_findings = clean_propn_token_array + stripped_matching # Adds stripped matching to clean_propn_token_array
    software_findings = RemoveDuplicate(software_findings) # Remove all duplicates from software_findings Array

    # Extracts each word within the input file as an array. Space characters used as a delimiter.
    url_array = UrlList(sentences) # FORCE URL FUNCTION FILL instead of regex
    if url_array: # If there are values in the URL array
        information_webpage = ArrayMode(url_array) # Set information_webpage by using the ArrayMode
        information_webpage = information_webpage.replace('\n', '') # Remove new line character from variable
    else: # If no URL variables exist
        information_webpage = "Unknown" # Set to Unknown
    
    restriction_sentence_dict,rxion_array = ProcessRestrictions(document, pos, neg, rxion_dict) # Processes restrictions via processrestrictions and stores sentence dictionary
    rxion_array_string = ArrayToString(RemoveDuplicate(rxion_array)) # Sets restriction array to string value

    fields = ["Software name", "Publisher","Information Webpage",  "Licensing Restrictions"] # Establishes field names for titles
    selected_variables_dict = {"software name": software_name, "publisher": publisher_name, "information webpage": information_webpage, "licensing restrictions": rxion_array_string} # Stores all discovered variables for the job
    field_variables_dict = {"software name": software_findings, "publisher": RemoveDuplicate(organization_entity_array), "information webpage": RemoveDuplicate(url_array)} # Defines output information dictionary
    
    return [os.path.basename(jobfile),selected_variables_dict,fields,rxion_array,field_variables_dict,restriction_sentence_dict,text] # Return job data to Django
def ProcessInputFile(inputfilename): # Determines file type and conversion steps
    if inputfilename.endswith('.txt'): # Checks to see if filetype is text file
        try:
            open_file = open(inputfilename).read() # Attempts to load text file without conversion
        except:
            open_file = ConvertAnsi(inputfilename) # Sets openfile to ANSI converted copy
        return open_file
    elif inputfilename.endswith('.docx'): # Check if document is Word Document
        open_file = docx2txt.process(inputfilename) # stores opened word document as variable
        return open_file
    elif inputfilename.endswith('.pdf'): # Check if document is a PDF
        pdf = wi(filename = inputfilename, resolution = 300) # Processes PDF and converts to image for further processing
        pdfImg = pdf.convert('jpeg') # Converts image to jpeg format
        open_file = "" # Defines string variable to store text
        for img in tqdm(pdfImg.sequence, desc=os.path.basename(inputfilename)): # For each image (page)
            page = wi(image = img) # Sets image to page variable
            pic = im.open(io.BytesIO(page.make_blob('jpeg'))) # Opens image and stores in pic variable
            text = tess.image_to_string(pic, lang = 'eng') # Processes image through tesseract and stores extracted text as a variable
            open_file += text # Concatenate extracted text to the full string file
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
def ParagraphParse(ocr_input): # Splits paragraphs before processing text
    all_paragraphs = re.split('\n{2,}', ocr_input) # Splits paragraphs by multiple newline characters
    parsed_paragraphs = "" # Sets variable for the parsed paragraphs
    for paragraph in all_paragraphs: # For each paragraph
        paragraph = paragraph.replace("\n", " ") # Replaces newline characters with spaces
        parsed_paragraphs += str(paragraph) + "\n\n" # Concatenates paragraph to paragraph string with new line character at the end    
    return parsed_paragraphs # returns paragraphs
def BulletUpperRemove(textinput): # Removes bulleted items and calls paragraph to lower
    ex_bulleted_text = re.sub(r'\([A-z0-9]{1,3}?\)',"",textinput) # Remove (a), (b), (iii) bulleting
    caps_to_lower_text = re.sub(r'\b[A-Z]{2,}\b',ParagraphToLower,ex_bulleted_text) # Change full uppercase paragraphs to lower
    return caps_to_lower_text # Returns lower case strings
def ParagraphToLower(m): # Changes full uppercase paragraphs to lower.
    return m.group(0).lower() # Returns lower case paragraphs
def UrlList(sentences): # Generates listing of websites identified in the document
    from spacy import attrs # Imports spacy attributes function to find specific attributes
    UrlList = [] # Defines array for discovered URLs
    for sentence in sentences: # For each sentence
        doc = nlp(str(sentence)) # Sets NLP sentence object to variable
        for token in doc: # For each sentence in document
            if token.like_url == True: # If the sentenece matches the URL attribute
                UrlList.append(token.text) # Store URL in array
    return UrlList # Return URL array
def RemoveNewLine(s): # Removes new line characters from strings
    return re.sub(r'\n{1,}'," ",str(s)) # Returns lines without excessive newline characters
def ProcessRestrictions(document, pos_trigger_words, neg_trigger_words, rxion_patterns): # Establishes restriction variables and executes each type
    rxion_array = [] # Defines restriction array to store restrictions found for each file
    restriction_sentence_dict = dict() # Defines restriction sentence dictionary that uses the restriction name as a key    
    for rxion in rxion_patterns: # Loops through restriction types to determine if the restriction applies to the document
        rxiontmp = ProcessRestrictionType(document,rxion_patterns[str(rxion)],pos_trigger_words,neg_trigger_words,str(rxion)) # Returns restriction type to document
        if rxiontmp: # If the document contains any sentences with the restriction type
            rxion_array.append(str(rxion)) # Append the restriction type string to the array
            restriction_sentence_dict[str(rxion)] = RemoveDuplicate(rxiontmp) # Append all unique sentences found for the restriction type to the dictionary
    if not rxion_array: # If no restriction types were identified
        rxion_array.append("Needs Review") # Set the restrictions to "needs review"
    return restriction_sentence_dict, rxion_array # Returns restriction sentences and restriction types array
def ProcessRestrictionType(document,restrictions,pos,neg,restrictionString): # Function to find restriction sentences
    rxion_sentences_array = [] # Define the array to store sentences flagged for the restriction type
    rx_array = [(p,n,r) for p in pos for n in neg for r in restrictions] #sets all variables in custom array for processing
    for sent in document.sents: # Loops through each sentence in the document
        sentence = str(sent).lower() # converts the sentence to lower to be compatible with term matching
        for rx in rx_array: # For each pos, neg, restriction term combination
            if rx[2] in sentence: # If there is a restriction term in the sentence
                if any(pattern in restrictionString.lower() for pattern in neg): # If there are any negative terms in the restriction type (NO RDP), ONLY search for RESTRICTED ITEMS
                    if rx[0] in sentence and str(sent) not in rxion_sentences_array:# and str(sent) not in rxion_sentences_array: # If there is both a positive and negative trigger word, and the sentence has not been flagged.
                        reg_pattern = re.compile(rx[1] + r"(.*" + rx[0] + r")?.*" + rx[2]) # If sentence contains negative, positive, then restriction (NOT...ALLOWED...REMOTE)
                        reg_pattern_rev = re.compile(rx[2] + r".*" + rx[1] + r"(.*" + rx[0] + r")?") # If sentence contains restriction, negative, then positive (REMOTE...NOT...ALLOWED)
                        if re.search(reg_pattern,sentence): # If first search version found
                            rxion_sentences_array.append(str(sent)) # Append to sentence array
                        elif re.search(reg_pattern_rev,sentence): # If second (reverse negative) found
                            rxion_sentences_array.append(str(sent)) # Append to sentence array
                    elif rx[0] not in sentence and str(sent) not in rxion_sentences_array:# and str(sent) not in rxion_sentences_array: # If only a negative and restriction term are in sentence and sentence has not been flagged.
                        reg_pattern = re.compile(rx[1] + r"(.*" + rx[0] + r")?.*" + rx[2]) # If sentence contains negative, then restriction (No...Remote)
                        reg_pattern_rev = re.compile(rx[2] + r".*" + rx[1] + r"(.*" + rx[0] + r")?") # If sentence contains restriction, then negative (Remote...Prohibited)
                        if re.search(reg_pattern,sentence): # If first search version found
                            rxion_sentences_array.append(str(sent)) # Append to sentence array
                        elif re.search(reg_pattern_rev,sentence): # If second search version found
                            rxion_sentences_array.append(str(sent)) # Append to sentence array
                elif rx[0] in sentence and str(sent) not in rxion_sentences_array:# and str(sent) not in rxion_sentences_array: # All sentences containing a positive trigger
                    reg_pattern = re.compile(r"("+ rx[1] + r".*)?" + rx[0] + r".*" + rx[2]) # If sentence contains an optional negative, positive, then restriction (grants...remote)
                    reg_pattern_rev = re.compile(rx[2] + r"(.*" + rx[1] + r".*)?" + rx[0]) # If sentence contains restriction, optional negative, then positive (remote...allowed)
                    if re.search(reg_pattern,sentence): # If first search version found
                        rxion_sentences_array.append(str(sent)) # Append to sentence array
                    elif re.search(reg_pattern_rev,sentence): # If second search version found
                        rxion_sentences_array.append(str(sent)) # Append to sentence array
                elif str(sent) not in rxion_sentences_array and str(sent) not in rxion_sentences_array: # If there is a restriction term and the sentence has not been flagged
                    rxion_sentences_array.append(str(sent)) # Append to the sentence array
    if len(rxion_sentences_array) > 0: # If sentences were flagged during the search
        return rxion_sentences_array # Return the sentence array
def HighlightText(usertext): # Returns inputted text as yellow for easy identification
    return Fore.YELLOW + str(usertext) + Fore.RESET # Returns highlighed characters
def StrongText(usertext,fcolor): # Returns strong tag for easy identification in HTML    
    return '<mark style="background-color:'+fcolor+'; border-radius: 10px;" ><strong><em>' + str(usertext) + "</em></strong></mark>" # Returns string contained in HTML tags
def ArrayMode(list): # Assists in determining entities from the AseulaMain
    try:
        return(mode(list)) # Returns the array value that appears the most
    except:
        return str("Unknown") # Returns unknown if the mode function errors
def RemoveDuplicate(array): # Removes duplicate elements in an array.
    array = list(dict.fromkeys(array)) # Removes duplicate array items
    return array
def ArrayToString(array): # Converts an array to a string.
    array_string = "" # Defines empty string
    i = 0
    while i <= (len(array)-1): # While array element is less than array length
        if (i != (len(array)-1)):  # If element is not the last item in array
            array_string += array[i] + ", " # Concatenate array item plus comma
        elif (i == (len(array)-1)): # If element is the last element in array
            array_string += array[i] # Concatenate array item without comma
        i += 1 # Add to i
    return array_string
def XlsxDump(jobDataArray): # Output to CSV for download and site import
    wb = Workbook() # Establishes workbook object format for sharepoint list
    ws = wb.active 
    ws.append(["Software Name", "Publisher Name", "Information Webpage", "Licensing Restrictions"]) # Appends header to ws object
    for job in jobDataArray: # Loops through each job
        ws.append([job[1]["software name"], job[1]["publisher"], job[1]["information webpage"], job[1]["licensing restrictions"]]) # Appends data from each job to line in ws object
    tab = Table(displayName="Table1", ref="A1:D" + str(len(jobDataArray)+1)) # Defines table dimensions
    ws.add_table(tab) # Adds table dimensions to ws object
    wb.save("./xlsx_dump.xlsx") # Saves excel table document
    # wb.save("media/xlsx_dump.xlsx") # FOR DJANGO

###############################################    DJANGO FRAMEWORK EXECUTION    ###############################################
#  if the database gets corrupted, use the script below to re-establish default values after clearing all cache files          #
################################################################################################################################

# # IMPORT PATTERNS
# rxion_patterns = {}
# pos_trigger_words = ["only", "grant", "grants", "granting", "granted", "allow", "allows", "allowing", "allowed", "permit", \
#     "permits", "permitting", "permitted", "require", "requires", "requiring", "required", "authorize", "authorizes", \
#         "authorizing", "authorized", "necessary"]
# neg_trigger_words = ["no", "not", "may not", "not granted", "not allowed", "not permitted", "forbidden", "restricts", "restricted",\
#         "prohibits", "prohibited"]
# rxion_patterns["Instructional-use only"] = ["teaching", "teaching use", "teaching-use", "instruction", "instructional use",\
#         "instructional-use", "instructional purposes", "academic", "academic use", "academic-use", "academic instruction",\
#             "academic institution", "academic purposes", "educational", "educational use", "educational-use",\
#                 "educational instruction", "educational institution", "institution", "educational purposes"]
# rxion_patterns["Research-use only"] = ["research", "research use", "research-use"]
# rxion_patterns["Requires Physical Device"] = ["activation key", "dongle","hardware"]
# rxion_patterns["No RDP use"] = ["remote", "rdp", "remote access", "remote-access", "remote desktop", "remote interface"]
# rxion_patterns["Use geographically limited (Campus)"] = ["designated site", "customer's campus", "internally","campus","facility"]
# rxion_patterns["Use geographically limited (radius)"] = ["radius", "limited radius", "geographically limited radius",\
#         "geographically-limited radius", "particular geography", "site license", "site licenses"]
# rxion_patterns["US use only"] = ["united states", "united states use", "u.s.", "u.s. use","export"]
# rxion_patterns["VPN required off-site"] = ["vpn", "virtual private network", "remote access"]
# rxion_patterns["Block embargoed countries"] = ["embargo", "embargoed", "embargoed country","export","countries"]
# rxion_patterns["Block use from Persons of Concern"] = ["person of concern", "persons of concern", "people of concern",\
#     "denied persons","person","entity"]
# rxion_patterns["On-site (lab) use only"] = ["lab-use"]
# rxion_patterns["On-site use for on-site students only"] = ["single fixed geographic site", "fixed geographic site",\
#         "geographic site", "on-site", "on-site use"]
# rxion_patterns["Virtualization Allowed"] = ["virtualization", "virtualizing", "multiplexing", "pooling"]


# for pattern in rxion_patterns:
#     print("----",pattern)
#     restrictionTitle.objects.create(restriction=pattern)
#     for term in rxion_patterns[pattern]:
#         print(term)
#         r_id = restrictionTitle.objects.get(restriction=pattern)
#         restrictionTerm.objects.create(restriction=r_id, restrictionterm=term)
# for pattern in pos_trigger_words:
#     print(pattern)
#     positiveTerm.objects.create(posterm=pattern)
# for pattern in neg_trigger_words:
#     print(pattern)
#     negativeTerm.objects.create(negterm=pattern)
# infoFieldCategory.objects.create(categoryname="software name")
# infoFieldCategory.objects.create(categoryname="publisher")
# infoFieldCategory.objects.create(categoryname="information webpage")
# infoFieldCategory.objects.create(categoryname="licensing restrictions")

# # Execution

# queuearray = [str(jobData.objects.get(pk=21).filefield.path)]

# print(queuearray[0])
# AseulaMain(queuearray[0])