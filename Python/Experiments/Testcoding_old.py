# /// Packages to install \\\
# pip install spacy
# python -m spacy download en_core_web_sm
# pip install docx2txt
# pip install PyPDF2

from colorama import Fore, Back, Style
import io, os, sys, re, timeit, statistics, docx2txt, PyPDF2, re, spacy, pytesseract as tess, platform
from spacy.lang.en import English
from re import search
from statistics import mode
from wand.image import Image as wi
from tqdm import tqdm # Progress Bar (pip install tqdm)
from colored import fg, bg, attr # Text color change (pip install colored)
from PIL import Image as im

##############################################    SCRIPT CONFIG    ############################################
current_sys = platform.system()
if current_sys.lower() == "windows":
    if os.path.isfile(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' #WINDOWS DEFAULT INSTALL
    elif os.path.isfile(r'C:\Users\Socce\AppData\Local\Tesseract-OCR\tesseract.exe'):
        tess.pytesseract.tesseract_cmd = r'C:\Users\Socce\AppData\Local\Tesseract-OCR\tesseract.exe' #WINDOWS USER INSTALL
    else:
        tess.pytesseract.tesseract_cmd = input("Please enter the tesseract.exe file path: ")
elif current_sys.lower() == "linux":
    tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' #LINUX

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_sm')

# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))

###############################################    FUNCTIONS    ###############################################
    
def ProcessInputFile(inputfilename):
    # Checks the input file's format, converts it if necessary, opens it, and initializes the Spacy loader for the specified file.
    # Checks if the input file is .txt.
    if inputfilename.endswith('.txt'):
        # Opens the .txt file.
        open_file = open(inputfilename).read()
        # Performs NLP on the .txt file.
        return open_file
    # Checks if the input file is .docx.
    elif inputfilename.endswith('.docx'):
        # Converts the .docx file to plaintext.
        open_file = docx2txt.process(inputfilename)
        # Performs NLP on the converted plaintext.
        return open_file
    # Checks if the input file is .pdf.
    elif inputfilename.endswith('.pdf'):
        # # Saves the filename to a variable and establishes image resolution.
        pdf = wi(filename = inputfilename, resolution = 300)
        # Converts pdf to jpeg.
        pdfImg = pdf.convert('jpeg')
        # Establishes a variable to hold JPEG text.    
        open_file = ""
        # Loops through each image (one image per page) for the input PDF document.
        #for img in pdfImg.sequence: #2.305 MINUTES
        #for img in tqdm(pdfImg.sequence, ascii=True, desc=inputfilename): #2.28 MINUTES
        for img in tqdm(pdfImg.sequence, desc=os.path.basename(inputfilename)): #2.274 MINUTES
            # ProgressBar(pdfImg.sequence.index(img),len(pdfImg.sequence))
            page = wi(image = img)
            # Opens image.
            pic = im.open(io.BytesIO(page.make_blob('jpeg')))
            # Performs text recognition on the open image.
            text = tess.image_to_string(pic, lang = 'eng')
            # Appends text from image to open_file string.
            open_file += text            
        return open_file

    else:
        # Prints an error message if the input file does not match one of the supported formats.
        print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")

def paragraph_parse(ocr_input):    
    all_paragraphs = re.split('\n{2,}', ocr_input)
    parsed_paragraphs = ""
    for paragraph in all_paragraphs:
        paragraph = paragraph.replace("\n", " ")
        parsed_paragraphs += str(paragraph) + "\n"    
    return parsed_paragraphs

def URLList(sentences):
    from spacy import attrs
    URLList = []    
    for sentence in sentences:
        doc = nlp(str(sentence))
        for token in doc:
            if token.like_url == True:
                URLList.append(token.text)
    return URLList

def ASEULA_Function(document):    
    #**********************************************    Organization     ***************************************************#
    # Establishes variable to store matching entities.
    organization_entity_array = []
    # Establishes a variable to hold search patterns.
    publisher_patterns = ["inc", "inc.","llc","incorporated", "©", "copyright"]
    # Iterates through each entity in the input file.
    for entity in document.ents:
        # Checks if entities in input file have the ORG label.
        if entity.label_ == "ORG":
            if any(pattern in entity.text.lower() for pattern in publisher_patterns):
                for element in publisher_patterns:
                    if entity.text != element:
                        organization_entity_array.append(entity.text)
        

        # Appends all entities with ORG label that contain any elements from the publisher_patterns array to the organization_entiity_array array.
        
        # #SEARCH STRING FOR ENTITIES
        # if "org" in entity.label_.lower():
        # if "autodesk" in entity.text.lower():
        #     print(f'{entity.text:{30}} {entity.label_:{30}} ')
        # print(f'{entity.text.title():{30}} {entity.label_:{30}} ')
                    
    # Checks if organization_entity_array is empty. Prints mode of the array if elements exist.
    if organization_entity_array:
        # Sets publisher_name as the mode of organization_entity_array.
        publisher_name = array_mode(organization_entity_array)
        publisher_name = publisher_name.replace('\n', ' ')
    else:
        # Sets publisher_name as "Unknown."
        publisher_name = "Unknown"
    org_findings = remove_duplicate(organization_entity_array)

    #**********************************************  Software Name   ***************************************************#
    
    # Establishes variable to store matching entities.
    person_entity_string = ""
    # Iterates through each entity in the input file.
    for entity in document.ents:
        # Checks if entities in input file have the PERSON label.
        if entity.label_ == "PERSON":
            # Appends entities to the person_entity_string variable.
            person_entity_string += entity.text + "\n"
    # Must perform NLP on string again because it does not carry over from original input file.
    propn_check = nlp(person_entity_string)

    # Establishes variable to store matching entities.
    propn_token_array = []
    # Iterates through each token in the input file.
    for token in propn_check:
        # Checks if entities with the PERSON label have PROPN part of speech.
        if token.pos_ == "PROPN":
            # Appends all entities with PERSON label and PROPN part of speech to an array.
            propn_token_array.append(token.text)
    # Checks if the propn_token_array is empty. Prints mode of the array if elements exist.
    clean_propn_token_array = remove_duplicate(propn_token_array)
    matching = [item for item in clean_propn_token_array if item in publisher_name]
    # Removes any duplicate array elements from matching.
    stripped_matching = remove_duplicate(matching)
    if matching:
        # Sets software_name as the string for the stripped_matching array.
        software_name = array_to_string(stripped_matching)
    elif not matching:
        # Sets software_name as the mode of propn_token_array.
        software_name = array_mode(propn_token_array)
    else:
        # Sets software_name as "Unknown."
        software_name = "Unknown"
    software_findings = clean_propn_token_array + stripped_matching
    software_findings = remove_duplicate(software_findings)

    #**********************************************    Website    ***************************************************#
   
    # Extracts each word within the input file as an array. Space characters used as a delimiter.
    url_array = URLList(sentences) # FORCE URL FUNCTION FILL instead of regex

    # Checks if url_array is empty. Prints mode of the array if elements exist.
    if url_array:
        # Sets information_webpage as the mode of url_array.
        information_webpage = array_mode(url_array)
        # Removes any line breaks in the extracted URL.
        information_webpage = information_webpage.replace('\n', '')
    else:
        # Sets information_webpage as "Unknown."
        information_webpage = "Unknown"
    url_findings = remove_duplicate(url_array)

    #**********************************************    Restrictions    ***************************************************#

    # Establishes variables to store restriction patterns and trigger words.
    # rxions = ["rxion_instructional_patterns","rxion_research_patterns","rxion_physical_patterns","rxion_rdp_patterns","rxion_campus_patterns","rxion_radius_patterns","rxion_us_patterns","rxion_vpn_patterns","rxion_embargo_patterns","rxion_poc_patterns","rxion_lab_patterns","rxion_site_patterns"]
    # rxions_output = ["Instructional-use only","Research-use only","Requires Physical Device","No RDP use","Use geographically limited (Campus)","Use geographically limited (radius)","US use only","VPN required off-site","Block embargoed countries","Block use from Persons of Concern","On-site (lab) use only","On-site use for on-site students only"]
    
    pos_trigger_words = ["only","grant","allow","permit","granting"]
    neg_trigger_words = ["may not", "not permitted", "not allowed", "forbidden", "restricts", "restricted", "prohibits", "prohibited"]
    rxion_instructional_patterns = ["teaching", "teaching use", "teaching-use", "instructional use", "instructional-use", \
    "academic use", "academic-use", "academic instruction", "academic institution", "educational instruction", "educational institution"]
    rxion_research_patterns = ["research", "research use", "research-use"]
    rxion_physical_patterns = ["activation key"]
    rxion_rdp_patterns = ["remote access", "remote-access", "remote desktop"]
    rxion_campus_patterns = ["designated site"]
    rxion_radius_patterns = ["radius"]
    rxion_us_patterns = []
    rxion_vpn_patterns = ["vpn","networked","remote access"]
    rxion_embargo_patterns = []
    rxion_poc_patterns = []
    rxion_lab_patterns = []
    rxion_site_patterns = []

    rxion_instructional_sentences = []
    rxion_research_sentences = []
    rxion_physical_sentences = []
    rxion_rdp_sentences = []
    rxion_campus_sentences = []
    rxion_radius_sentences = []
    rxion_us_sentences = []
    rxion_vpn_sentences = []
    rxion_embargo_sentences = []
    rxion_poc_sentences = []
    rxion_lab_sentences = []
    rxion_site_sentences = []
    
    rxion_array = []    
    # rxion_sentence_array = []
       
    for sentence in document.sents:
        sentence_string = str(sentence) 
        sentence_lower = sentence_string.lower()
        if any(pattern in sentence_lower for pattern in rxion_instructional_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Instructional-use only")
                rxion_instructional_sentences.append(sentence)
                print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_research_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Research-use only")
                rxion_research_sentences.append(sentence)
                print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_physical_patterns):
            rxion_array.append("Requires Physical Device")
            rxion_physical_sentences.append(sentence)
            print(HighlightText(sentence_string))       
        if any(pattern in sentence_lower for pattern in rxion_rdp_patterns):
            if any(pattern in sentence_lower for pattern in neg_trigger_words):
                rxion_array.append("No RDP use")
                rxion_rdp_sentences.append(sentence)
                print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_campus_patterns):
            rxion_array.append("Use geographically limited (Campus)")
            rxion_campus_sentences.append(sentence)  
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_radius_patterns):
            rxion_array.append("Use geographically limited (radius)")
            rxion_radius_sentences.append(sentence)
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_us_patterns):
            rxion_array.append("US use only")
            rxion_us_sentences.append(sentence)
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_vpn_patterns):
            rxion_array.append("VPN required off-site")
            rxion_vpn_sentences.append(sentence)
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_embargo_patterns):
            rxion_array.append("Block embargoed countries")
            rxion_embargo_sentences.append(sentence)
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_poc_patterns):
            rxion_array.append("Block use from Persons of Concern")
            rxion_poc_sentences.append(sentence)
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_lab_patterns):
            rxion_array.append("On-site (lab) use only")
            rxion_lab_sentences.append(sentence)
            print(HighlightText(sentence_string))
        if any(pattern in sentence_lower for pattern in rxion_site_patterns):
            rxion_array.append("On-site use for on-site students only")
            print(HighlightText(sentence_string))
            rxion_site_sentences.append(sentence)
        # else:
        #     print(sentence_string)
    # i = 1
    # for element in rxion_sentence_array:
    #     print(rxion_array)
    #     print(i, " --- " ,element)
    #     i += 1

    if not rxion_array:        
        rxion_array.append("Needs Review")

    string_rxion_array = array_to_string(remove_duplicate(rxion_array))

    fields = ["Url", "Software name", "Organization", "Restricitons"]
    selected_dict = {"url": information_webpage , "software name": software_name, "org": publisher_name, "restrictions": string_rxion_array}
    field_dict = {"url": url_findings, "software name": software_findings, "org": org_findings}
    sentence_dict = {"Instructional-use only": rxion_instructional_sentences,"Research-use only": rxion_research_sentences,"Requires Physical Device": rxion_physical_sentences, \
        "No RDP use": rxion_rdp_sentences,"Use geographically limited (Campus)": rxion_campus_sentences,"Use geographically limited (radius)": rxion_radius_sentences, \
        "US use only": rxion_us_sentences,"VPN required off-site": rxion_vpn_sentences,"Block embargoed countries": rxion_embargo_sentences, \
        "Block use from Persons of Concern": rxion_poc_sentences,"On-site (lab) use only": rxion_lab_sentences,"On-site use for on-site students only": rxion_site_sentences}


    return [os.path.basename(job),software_name,publisher_name,information_webpage, rxion_array, string_rxion_array, fields, selected_dict, field_dict, sentence_dict]

def OutputResults(job):
    print("\nHere's what we found for", job[0])
    print("-----------------------")
    # Prints all established variables for the input file.
    print("Software: ", job[7]["software name"])
    print("Publisher: ", job[7]["org"])
    print("Information Webpage: ", job[7]["url"])
    print("Licensing Restrictions: ", job[7]["restrictions"])
    print("-----------------------")
    user_input()

def HighlightText(usertext):
    from colorama import Fore, Back, Style
    return Fore.YELLOW + str(usertext).upper() + Fore.RESET

# Function that finds the mode of an array.
def array_mode(list): 
    return(mode(list))


# Function that removes duplicate elements in an array.
def remove_duplicate(array):
    array = list(dict.fromkeys(array))
    return array

# Function that returns array elements as string.
def array_to_string(array):
    array_string = ""
    i = 0
    while i <= (len(array)-1):
        if (i != (len(array)-1)):
            array_string += array[i] + ", "
        elif (i == (len(array)-1)):
            array_string += array[i]
        i += 1
    return array_string

def arrayFormatting(array):
    i=1
    for element in array:
        print (str(i) + ".", element)
        i+=1
    print ("\n")

def rxion_formatting(dictionary):
    new_rxion_array = []
    for key in dictionary:
        if key in job[4]:
            print (key)
            print("-----------------------")
            arrayFormatting(dictionary[key])
            user_selection = input("\nIs this restriction flagged correctly? (y/n)  ").lower().strip()
            if user_selection == "y":
                new_rxion_array.append(key)
            elif user_selection == "n":
                print ("This restriction will be unflagged\n")
    return new_rxion_array

def user_input():
    while True:
        info_check = str(input("Is the information above correct? (y/n)  ")).lower().strip()
        if info_check == "y":
            print ("Information will shortly pushed to SharePoint. Thank you for using ASEULA!")
            break
        elif info_check == "n":
            print ("\n")
            print (*job[6], sep= ", ")
            while True:
                field_correction = input("\nWhich of the fields information needs to be corrected?  ").lower().strip()
                if field_correction == "restrictions":
                    print ('\n')
                    print ('-' * 10)
                    new_rxion_array = rxion_formatting(job[9])
                    new_string_rxion_array = array_to_string(remove_duplicate(new_rxion_array))
                    job[7][field_correction] = new_string_rxion_array #selected_dict[field_correction] = new_string_rxion_array
                    OutputResults(job)
                    break
                elif field_correction == "org" or field_correction == "url" or field_correction == "software name":
                    print ('-' * 10)
                    incorrect_data = job[8][field_correction]
                    print (*incorrect_data, sep=", ")
                    user_selection = input("\nwhich value is correct?  ")
                    index_element = incorrect_data.index(user_selection)
                    job[7][field_correction] = incorrect_data[index_element]
                    OutputResults(job)
                    break
                else: 
                    print("Error! Invalid input. Please enter a valid field option.")
            break
        else:
            print('Invalid input. Please try again.')

###############################################    EXECUTION    ###############################################

# Accepts a file path as user input and strips it of quotation marks.
#Argument input for batch processing

filename_array = []
jobDataArray = []
jobSentenceArray = []
sentences = []
i = 0
if len(sys.argv) >= 2:    
    for filename in sys.argv[1:]:
        fileArray = []
        filename_array.append(filename.strip('"'))
        i += 1

else:
    print("\nASEULA alpha v.1 for",current_sys)
    filename_array = []
    fileInput = True
    while fileInput == True:        
        inputFile = input("\nPlease enter the absolute path for file #" + str(len(filename_array) + 1) + "(or press enter to continue): ")        
        if inputFile != "":
            filename_array.append(inputFile.strip('"'))
        else:            
            fileInput = False
    
if len(filename_array) > 0:
    start = timeit.default_timer()
    print("Please wait while we process",len(filename_array),"file(s)... \n")
    for job in filename_array:
        text = ProcessInputFile(job)
        text = paragraph_parse(text)
        document = nlp(text)
        sentences = []
        for sent in document.sents:
            sentences.append(sent) # Append sentences in array for future comparison
        jobDataArray.append(ASEULA_Function(document))        
        jobSentenceArray.append(sentences)          
        i += 1
else:
    print("\nNo input was provided. Thank you for using ASEULA!\n")

for job in jobDataArray:
    OutputResults(job)

#Process runtime output
# start = timeit.default_timer()
end = timeit.default_timer()
runtime = end - start
if runtime > 59:
    print("Job runtime: " + str(runtime/60) + " Minutes\n")
else:
    print("Job runtime: " + str(runtime) + " Seconds\n")

############################################    INACTIVE FUNCTIONS    ############################################

# Similarity check and sentence output
#Searches through all tokens to check similarity with restriction items.
def SimilarityValueList(sentences, restrictions):
    sent_count = 1
    for sentence in sentences:
        doc = nlp(str(sentence))
        rxsion = nlp(restrictions)
        rx_sim = 0
        for token in doc:
            for rx in rxsion:
                if rx.similarity(token) > .70:
                    print(f'{token.text:{15}}{rx.text:{15}}{rx.similarity(token) * 100}')
                    rx_sim = 1
        if rx_sim == 1:            
            #print(str(sent_count) + ". " + str(sentence))
            sent_count += 1

def SimilarityList(sentences, restrictions):
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

#Part of Speech Tagging
def PartofSpeechList(sentences):
    output_file = open("./newfile.csv","w+")    
    output_file.write("TEXT,LEMMA,POS,DEP,HEAD,HAS_VECTOR\n")
    for sentence in sentences:
        doc = nlp(str(sentence))        
        for token in doc:
            output_file.write(str(token.text) + "," + str(token.lemma_) + "," + str(token.pos_) + "," + str(token.dep_) + "," + str(token.head.text) + "," + str(token.has_vector) + "\n")
            #print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{15}} {token.head.text:{15}} {token.has_vector:{15}} ')
    output_file.close()
    

#Purge Stop Words
def PurgeStopList(sentences):
    for sentence in sentences:
        doc = nlp(str(sentence))
        purge_string = ""
        for token in doc:
            if token.is_stop == 'False':
                purge_string += str(token.text) + " "
            else:
                continue

#Lemmatization
def LemmaList(sentences):
    lemma_string = ""
    for sentence in sentences:
        doc = nlp(str(sentence))
        for token in doc:
            print(f'{token.text:{15}} {token.lemma_:{15}} ')
            lemma_string += str(token.lemma_) + " "
    return lemma_string

#Syntactic dependency
def SyntacticList(sentences):    
    for sentence in sentences:
        doc = nlp(str(sentence))
        for chunk in doc.noun_chunks:
            print(f'{chunk.text:{30}}{chunk.root.text:{15}}{chunk.root.dep_}')

#Output all token info
def TokenList(sentences):    
    for sentence in sentences:
        doc = nlp(str(sentence))
        for token in doc:
            print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{10}} {token.is_stop}')

def RemovePunct(sentstring):
    import string
    nopunct = ""
    sentstring = str(sentstring)
    for char in sentstring:
        if char not in string.punctuation:
            nopunct += char    
    return nopunct

#Named entity recognition ORG select
def NER_function(sentences):
    entities = []
    for sentence in sentences:
        sentence = RemovePunct(sentence)
        doc = nlp(str(sentence))
        for ent in doc.ents:
            publisher_patterns = ["Inc", "LLC","Inc.", "Incorporated", "©", "Copyright"]
            #FIND Orgs
            if ent.label_.lower() == "org" and any(pattern in ent.text for pattern in publisher_patterns):                
                for token in ent:
                    if token.pos_ == "PROPN" and token.dep_ == "compound" or token.dep_ == "ROOT":
                        entities.append(ent.text)
                        print(ent.text)
                    elif token.pos_ == "PUNCT":
                        entities.append(ent.text)
                        print(ent.text)

            elif ent.label_.lower() == "org":
                entities.append(ent.text)
                print(ent.text)
                #print(f'{ent.text:{30}} {ent.label_:{15}}')

        for token in doc:
            if token.text.title() in entities:
                if token.pos_ == "PROPN":
                    #print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{15}}')
                    continue
    print(array_mode(entities))

# from sense2vec import Sense2Vec
# s2v = Sense2Vec().from_disk("../../../s2v_reddit_2015_md")

# def FindSimilarTerms(inputarray):
#     from sense2vec import Sense2Vec
#     output_array = []    
#     for element in inputarray:
#         try:
#             output_array.append(element)
#             element = element.replace(" ","_")
#             #s2v = Sense2Vec().from_disk("../../../s2v_reddit_2019_lg")
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

# [('machine_learning|NOUN', 0.8986967),
#  ('computer_vision|NOUN', 0.8636297),
#  ('deep_learning|NOUN', 0.8573361)]

#################################  SANDBOX AREA #################################################

# RULES BASED MATCHER
# keysight_pub_pattern = [{'POS': 'PROPN', 'DEP': 'compound'},
#            {'POS': 'PROPN', 'DEP': 'ROOT'},
#            {'POS': 'PUNCT'},
#            {'POS': 'PROPN', 'DEP': 'appos'}]



# # # Displacy output to browser
# # from spacy import displacy
# # #Obtain IP for browser view
# # import socket
# # host_ip = socket.gethostbyname(socket.gethostname())
# # print("\nYour rendered strings will be located at the following address: "+ str(host_ip) + ":5000\n")
# # i = 1
# # for sentence in sentences:
# #     print("Sentence " + str(i) + " of " + str(len(sentences)))
# #     displacy.serve(sentence, style='dep') # OR ent
# #     input()

# #Tesseract output defaults to unicode that causes errors when executed by Windows
# #Convert_ansi detects if windows is being utilized and converts to an acceptable format
# # def convert_ansi(file_input):
# #     import codecs
# #     import platform
# #     current_sys = platform.system()
# #     inputfile = "./"+ file_input + ".txt"    
# #     outputfile = "./"+ file_input + "ansi.txt"
# #     if str(current_sys) == "Windows":
# #         print("The current OS is: " + current_sys + ". You must convert")
# #         with io.open( inputfile , mode='r', encoding='utf8') as fc:
# #             content = fc.read()
# #         with io.open( outputfile , mode='w', encoding='cp1252') as fc:
# #             fc.write(content)
# #         return str(outputfile)        
# #     else:
# #         return inputfile

# Semantic meaning extraction
# if negative semantic and restriction in sentence
#   Mark as prohibited restriction
# if positive semantic and restriction in sentence
#   Mark as allowed restriction

# RULE BASED extraction
# if negative statement > restriction in sentence
# if positive statement > restriction in sentence




# rxion_instructional_patterns = ["teaching","instruction","academic","education","research","remote_desktop"]
# SENSE2VEC
#https://github.com/explosion/sense2vec
# pip3 install sense2vec



# # Piped for spaCy
# from sense2vec import Sense2VecComponent
# nlp = spacy.load("en_core_web_lg")
# s2v = Sense2VecComponent(nlp.vocab).from_disk("../../../s2v_reddit_2015_md") # Mem usage peaks at 2.8GB
# #s2v = Sense2VecComponent(nlp.vocab).from_disk("../../../s2v_reddit_2019_lg") # MUST HAVE 16GB Ram Minimum
# nlp.add_pipe(s2v)
# doc = nlp("A sentence about natural language processing.") #Sentence that is being processed
# assert doc[3:6].text == "natural language processing" #Token in the sentence
# freq = doc[3:6]._.s2v_freq
# vector = doc[3:6]._.s2v_vec
# most_similar = doc[3:6]._.s2v_most_similar(10)
# print("The most similar words are: \n")
# for element in most_similar:
#     (terms, pos) = element[0]    
#     print(f'{terms:{40}}{element[1] * 100:{15}}')






    