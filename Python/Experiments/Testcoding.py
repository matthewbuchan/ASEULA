# /// Packages to install \\\
# pip install spacy
# python -m spacy download en_core_web_sm
# pip install docx2txt
# pip install PyPDF2


import io
import os
import sys
from time import sleep
import timeit
import spacy
from spacy.lang.en import English
import docx2txt
import PyPDF2
import re
from re import search
import statistics 
from statistics import mode
from wand.image import Image as wi
import pytesseract as tess
from tqdm import tqdm # Progress Bar (pip install tqdm)
from colored import fg, bg, attr # Text color change (pip install colored)
# #Windows
# tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#Linux
tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
from PIL import Image as im

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
                        organization_entity_array.append(entity.text)
                        # print(f'{entity.text:{30}} {entity.label_:{30}} ')
                    # print(f'{entity.text:{30}} {entity.label_:{30}} ')
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

    # Extracts each word within the input file as an array. Space characters used as a delimiter.
    token_split = document.text.split(" ")
    # Establiishes an empty array to hold all possible URL matches.
    url_array = []
    # Iterates through each item in the token_split array.
    for item in token_split:
        # Strips parentheses from each array item.
        stripped_item = item.strip('()')
        # Establishes a pattern to verify valid URLs.
        regex = re.compile(r'(https?://?\S+)')
    # Checks if any items in the token_split array match the regular expression (regex variable). If so, the list item is appended to the url_array array.
        if re.match(regex, stripped_item):
            url_array.append(stripped_item)
    
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

    # Establishes variables to store restriction patterns and trigger words.
    # rxions = ["rxion_instructional_patterns","rxion_research_patterns","rxion_physical_patterns","rxion_rdp_patterns","rxion_campus_patterns","rxion_radius_patterns","rxion_us_patterns","rxion_vpn_patterns","rxion_embargo_patterns","rxion_poc_patterns","rxion_lab_patterns","rxion_site_patterns"]
    # rxions_output = ["Instructional-use only","Research-use only","Requires Physical Device","No RDP use","Use geographically limited (Campus)","Use geographically limited (radius)","US use only","VPN required off-site","Block embargoed countries","Block use from Persons of Concern","On-site (lab) use only","On-site use for on-site students only"]
    
    pos_trigger_words = ["only"]
    neg_trigger_words = ["may not", "not permitted", "not allowed", "forbidden", "restricts", "restricted", "prohibits", "prohibited"]
    rxion_instructional_patterns = ["teaching", "teaching use", "teaching-use", "instructional use", "instructional-use", \
    "academic use", "academic-use", "academic instruction", "academic institution", "educational instruction", "educational institution"]
    rxion_research_patterns = ["research", "research use", "research-use"]
    rxion_physical_patterns = ["activation key"]
    rxion_rdp_patterns = ["remote access", "remote-access", "remote desktop"]
    rxion_campus_patterns = ["designated site"]
    rxion_radius_patterns = ["radius"]
    rxion_us_patterns = []
    rxion_vpn_patterns = ["vpn"]
    rxion_embargo_patterns = []
    rxion_poc_patterns = []
    rxion_lab_patterns = []
    rxion_site_patterns = []
    
    rxion_array = []
    rxion_sentence_array = []
    for sentence in document.sents:
        sentence_string = str(sentence) 
        sentence_lower = sentence_string.lower()
        if any(pattern in sentence_lower for pattern in rxion_instructional_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Instructional-use only")
                print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_research_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Research-use only")
                print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_physical_patterns):
            rxion_array.append("Requires Physical Device")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_rdp_patterns):
            if any(pattern in sentence_lower for pattern in neg_trigger_words):
                rxion_array.append("No RDP use")
                print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_campus_patterns):
            rxion_array.append("Use geographically limited (Campus)")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_radius_patterns):
            rxion_array.append("Use geographically limited (radius)")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_us_patterns):
            rxion_array.append("US use only")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_vpn_patterns):
            rxion_array.append("VPN required off-site")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_embargo_patterns):
            rxion_array.append("Block embargoed countries")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_poc_patterns):
            rxion_array.append("Block use from Persons of Concern")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_lab_patterns):
            rxion_array.append("On-site (lab) use only")
            print(HighlightText(sentence_string))
        elif any(pattern in sentence_lower for pattern in rxion_site_patterns):
            rxion_array.append("On-site use for on-site students only")
            print(HighlightText(sentence_string))
        else:
            print(sentence_string)
    if not rxion_array:        
        rxion_array.append("Needs Review")
    string_rxion_array = array_to_string(remove_duplicate(rxion_array))

    return [os.path.basename(job),software_name,publisher_name,information_webpage,string_rxion_array]

def OutputResults(job):
    print("\nHere's what we found for", job[0])
    print("-----------------------")
    # Prints all established variables for the input file.
    print("Software: ", job[1])
    print("Publisher: ", job[2])
    print("Information Webpage: ", job[3])
    print("Licensing Restrictions: ", job[4])
    print("-----------------------")

def HighlightText(sentence):
    highlight = fg('yellow')
    reset = attr('reset')
    return highlight + sentence + reset

#Similarity check and sentence output
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
    for sentence in sentences:
        doc = nlp(str(sentence))
        for token in doc:
            print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{15}} {token.has_vector:{15}} ')
    

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

def ask_user():
    yes_or_no = str(input("Is this information correct (y/n)? ")).lower().strip()
    try:
        if yes_or_no[0] == 'y':
            print("Thank you for using ASEULA! Your information will be pushed to SharePoint shortly!")
        elif yes_or_no[0] == 'n':
            print("We're sorry. Which field is incorrect?")
        else:
            print('Invalid input. Please try again.')
            return ask_user()
    except Exception as error:
        print("Please enter a valid character.")
        print(error)
        return ask_user()

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
    filename_array = []
    fileInput = True
    while fileInput == True:
        inputFile = input("\n\nPlease enter the absolute path for file #" + str(len(filename_array) + 1) + "(or press enter to continue): ")        
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
        #jobSentenceArray.append(sentences)
        i += 1
        
        # print(LemmaList(sentences))
        # NER_function(sentences)
        # SimilarityValueList(sentences)
        # PartofSpeechList(sentences)
        # Semantic()
        # rxsion = ("remote prohibit forbid")
        # SimilarityList(sentences, rxsion)
        # URLList(sentences)
        # #VectorSimilarityList(sentences)


else:
    print("\nNo input was provided. Thank you for using ASEULA!\n")

for job in jobDataArray:
    OutputResults(job)

# #Process runtime output
# # start = timeit.default_timer()
# end = timeit.default_timer()
# runtime = end - start
# if runtime > 59:
#     print("Job runtime: " + str(runtime/60) + " Minutes\n")
# else:
#     print("Job runtime: " + str(runtime) + " Seconds\n")

#################################  SANDBOX AREA #################################################

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

# from sense2vec import Sense2Vec
# s2v = Sense2Vec().from_disk("../../../s2v_reddit_2015_md")
# for element in rxion_instructional_patterns:
#     print(element)
#     query = str(element) + "|NOUN"
#     assert query in s2v
#     vector = s2v[query]
#     freq = s2v.get_freq(query)
#     most_similar = s2v.most_similar(query, n=10)
#     for phrase in most_similar:
#         print(phrase)
#     # [('machine_learning|NOUN', 0.8986967),
#     #  ('computer_vision|NOUN', 0.8636297),
#     #  ('deep_learning|NOUN', 0.8573361)]


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






    