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

# # Establishes variable for English sentence parsing method.
# sentence_parser = English()
# sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))
###############################################    FUNCTIONS    ###############################################

def ConvertAnsi(file_input):
    import codecs    
    inputfile = file_input    
    if current_sys.lower() == "windows":
        with io.open( inputfile , mode='r', encoding='utf8') as fc:
            content = fc.read()            
        return content
    else:
        return inputfile

def ProcessInputFile(inputfilename):
    if inputfilename.endswith('.txt'):
        open_file = ConvertAnsi(inputfilename)
        # open_file = open(inputfilename).read()
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

def ASEULAFunction(document,full_job_text):
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
    url_array = URLList(sentences) # FORCE URL FUNCTION FILL instead of regex    
    if url_array:        
        information_webpage = ArrayMode(url_array)        
        information_webpage = information_webpage.replace('\n', '')
    else:        
        information_webpage = "Unknown"

    # Establishes variables to store restriction patterns and trigger words.
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
    sentence_dict = dict()
    
    # Restriction runs
    rxiontmp = ProcessRestrictionType(document, rxion_instructional_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("Instructional-use only")
        sentence_dict['Instructional-use only'] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_research_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("Research-use only")
        sentence_dict['Research-use only'] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_physical_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("Requires Physical Device")
        sentence_dict['Requires Physical Device'] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_rdp_patterns,neg_trigger_words)
    if rxiontmp:
        rxion_array.append("No RDP use")
        sentence_dict['No RDP use'] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_campus_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("Use geographically limited (Campus)")
        sentence_dict["Use geographically limited (Campus)"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_radius_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("Use geographically limited (radius)")
        sentence_dict["Use geographically limited (radius)"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_us_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("US use only")
        sentence_dict["US use only"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_vpn_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("VPN required off-site")
        sentence_dict["VPN required off-site"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_embargo_patterns,neg_trigger_words)
    if rxiontmp:
        rxion_array.append("Block embargoed countries")
        sentence_dict["Block embargoed countries"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_poc_patterns,neg_trigger_words)
    if rxiontmp:
        rxion_array.append("Block use from Persons of Concern")
        sentence_dict["Block use from Persons of Concern"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_lab_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("On-site (lab) use only")
        sentence_dict["On-site (lab) use only"] = rxiontmp
    rxiontmp = ProcessRestrictionType(document, rxion_site_patterns,pos_trigger_words)
    if rxiontmp:
        rxion_array.append("On-site use for on-site students only")
        sentence_dict["On-site use for on-site students only"] = rxiontmp

    if not rxion_array:        
        rxion_array.append("Needs Review")

    string_rxion_array = ArrayToString(RemoveDuplicate(rxion_array))

    fields = ["Software name", "Publisher","Information Webpage",  "Licensing Restrictions"]
    selected_dict = {"software name": software_name, "publisher": publisher_name, "information webpage": information_webpage, "licensing restrictions": string_rxion_array}
    field_array_dict = {"software name": software_findings, "publisher": RemoveDuplicate(organization_entity_array), "information webpage": RemoveDuplicate(url_array)}

    return [os.path.basename(job),selected_dict,fields,rxion_array,field_array_dict,sentence_dict,full_job_text]

def ProcessRestrictionType(document,restrictions,posneg):
    patterns_array = []
    rxion_sentences_array = []
    for sentence in document.sents:
        sentence = str(sentence).lower()
        element_sentence = ""
        element_pattern = ""
        pattern_len = 0
        pattern_found = False
        #rxion_pattern = FindSimilarTerms(restrictions)
        if any(pattern.lower() in sentence for pattern in posneg) and any(pattern.lower() in sentence for pattern in restrictions):
            element_sentence = sentence
            pattern_found = True
            # for element in posneg:
            #     for pattern in restrictions:
            #         reg_pattern = re.compile(element +r"\b(\W*\w*\W*?){1,7}\b"+ pattern)
            #         reg_pattern_rev = re.compile(pattern +r"\b(\W*\w*\W*?){1,7}\b"+ element)
            #         if re.search(reg_pattern,sentence.lower()): #  and pattern_found == False
            #             pattern_string = str(re.search(reg_pattern,sentence).group())
            #             if len(pattern_string) > pattern_len:
            #                 element_sentence = sentence.replace(pattern_string,HighlightText(pattern_string))
            #                 #print(element_sentence)
            #             pattern_found = True

            #         if re.search(reg_pattern_rev,sentence.lower()):
            #             pattern_string = str(re.search(reg_pattern_rev,sentence).group())
            #             if len(pattern_string) > pattern_len:
            #                 element_sentence = sentence.replace(pattern_string,HighlightText(pattern_string))
            #                 #print(element_sentence)
            #             pattern_found = True
        else:
            if any(pattern.lower() in sentence for pattern in restrictions):
                element_sentence = sentence
                pattern_found = True
            # for pattern in restrictions:
            #     if pattern.lower() in sentence:
                    
            #         element_sentence = sentence.replace(pattern, HighlightText(pattern))
            #         pattern_found = True

        if pattern_found == True:            
            rxion_sentences_array.append(element_sentence)
            patterns_array.append(element_pattern)

    if len(rxion_sentences_array) > 0:        
        rxionjob_sentence_array.append(rxion_sentences_array)
        return rxion_sentences_array

def OutputResults(job):
    print("\nHere's what we found for", job[0])
    print("-----------------------")    
    print("Software: ", job[1]['software name'])
    print("Publisher: ", job[1]['publisher'])
    print("Information Webpage: ", job[1]['information webpage'])
    print("Licensing Restrictions: ", job[1]['licensing restrictions'])
    print("-----------------------")
    UserVerification()

def UserVerification():
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
                    job[1][job[2][field_correction - 1].lower()] = ArrayToString(RemoveDuplicate(new_rxion_array)) #selected_dict[field_correction] = new_string_rxion_array
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
    return Fore.YELLOW + str(usertext).upper() + Fore.RESET

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
        jobDataArray.append(ASEULAFunction(document, full_job_text))
        i += 1
else:
    print("\nNo input was provided. Thank you for using ASEULA!\n")

for job in jobDataArray:
    OutputResults(job)

if len(filename_array) > 0:
        # Print runtime output
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

#Remove punctuation from string
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
    print(ArrayMode(entities))

# from sense2vec import Sense2Vec
# s2v = Sense2Vec().from_disk("../../../s2v_reddit_2015_md")

def FindSimilarTerms(inputarray):
    from sense2vec import Sense2Vec
    output_array = []    
    for element in inputarray:
        try:
            output_array.append(element)
            element = element.replace(" ","_")
            #s2v = Sense2Vec().from_disk("../../../s2v_reddit_2019_lg")
            s2v = Sense2Vec().from_disk("../../../s2v_reddit_2015_md")
            query = str(element) + "|NOUN"
            assert query in s2v
            vector = s2v[query]
            freq = s2v.get_freq(query)
            most_similar = s2v.most_similar(query, n=5)
            for i in most_similar:            
                i = i[0].split("|")
                i = i[0].replace("_"," ").lower()
                output_array.append(i)                
        except:
            pass
    if output_array > inputarray:
        return output_array
    else:
        return inputarray

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


# SENSE2VEC
#https://github.com/explosion/sense2vec
# pip3 install sense2vec