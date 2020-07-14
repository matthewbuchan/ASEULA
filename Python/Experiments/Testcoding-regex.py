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
    tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' #WINDOWS
elif current_sys.lower() == "linux":
    tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' #LINUX

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_sm')

# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))

###############################################    FUNCTIONS    ###############################################

# Checks the input file's format, converts it if necessary, opens it, and initializes the Spacy loader for the specified file.
def ProcessInputFile(inputfilename):
    if inputfilename.endswith('.txt'):
        open_file = open(inputfilename).read()
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

def ASEULA_Function(document):    
    # Establish variables to store publisher
    organization_entity_array = []
    publisher_patterns = ["inc", "inc.","llc","incorporated", "©", "copyright"]
    for entity in document.ents:
        # Checks if entities in input file have the ORG label.
        if entity.label_ == "ORG":
            if any(pattern in entity.text.lower() for pattern in publisher_patterns):
                for element in publisher_patterns:
                    if entity.text != element:
                        organization_entity_array.append(entity.text)
                    
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
    
    # Restriction runs
    if ProcessRestrictionType(document, rxion_instructional_patterns,pos_trigger_words):
        rxion_array.append("Instructional-use only")
    if ProcessRestrictionType(document, rxion_research_patterns,pos_trigger_words):
        rxion_array.append("Research-use only")
    if ProcessRestrictionType(document, rxion_physical_patterns,pos_trigger_words):
        rxion_array.append("Requires Physical Device")
    if ProcessRestrictionType(document, rxion_rdp_patterns,neg_trigger_words):
        rxion_array.append("No RDP use")            
    if ProcessRestrictionType(document, rxion_campus_patterns,pos_trigger_words):
        rxion_array.append("Use geographically limited (Campus)")
    if ProcessRestrictionType(document, rxion_radius_patterns,pos_trigger_words):
        rxion_array.append("Use geographically limited (radius)")
    if ProcessRestrictionType(document, rxion_us_patterns,pos_trigger_words):
        rxion_array.append("US use only")            
    if ProcessRestrictionType(document, rxion_vpn_patterns,pos_trigger_words):
        rxion_array.append("VPN required off-site")            
    if ProcessRestrictionType(document, rxion_embargo_patterns,neg_trigger_words):
        rxion_array.append("Block embargoed countries")
    if ProcessRestrictionType(document, rxion_poc_patterns,neg_trigger_words):
        rxion_array.append("Block use from Persons of Concern")
    if ProcessRestrictionType(document, rxion_lab_patterns,pos_trigger_words):
        rxion_array.append("On-site (lab) use only")
    if ProcessRestrictionType(document, rxion_site_patterns,pos_trigger_words):
        rxion_array.append("On-site use for on-site students only")

    if not rxion_array:        
        rxion_array.append("Needs Review")

    string_rxion_array = array_to_string(remove_duplicate(rxion_array))

    return [os.path.basename(job),software_name,publisher_name,information_webpage,string_rxion_array]

def ProcessRestrictionType(document,restrictions,posneg):
    rxion_sentences_array = []
    for sentence in document.sents:
        sentence = str(sentence).lower()
        element_sentence = ""
        pattern_found = False
        #rxion_pattern = FindSimilarTerms(restrictions)
        if any(pattern.lower() in sentence for pattern in posneg) and any(pattern.lower() in sentence for pattern in restrictions):
            for element in posneg:
                for pattern in restrictions:
                    reg_pattern = re.compile(element + r"(\W*\w*\W*?){,4}" + pattern)
                    reg_pattern_rev = re.compile(pattern + r"(\W*\w*\W*?){,4}" + element)
                    if re.search(reg_pattern,sentence.lower()): #  and pattern_found == False
                        pattern_sentence = str(re.search(reg_pattern,sentence).group())
                        if len(pattern_sentence) > len(element_sentence):
                            element_sentence = sentence.replace(pattern_sentence,HighlightText(pattern_sentence))
                        pattern_found = True

                    if re.search(reg_pattern_rev,sentence.lower()):
                        pattern_sentence = str(re.search(reg_pattern_rev,sentence).group())
                        if len(pattern_sentence) > len(element_sentence):
                            element_sentence = sentence.replace(pattern_sentence,HighlightText(pattern_sentence))
                        pattern_found = True
        else:
            for pattern in restrictions:
                if pattern.lower() in sentence:
                    element_sentence = sentence.replace(pattern, HighlightText(pattern))
                    pattern_found = True

        if pattern_found == True:
            rxion_sentences_array.append(element_sentence)

    if len(rxion_sentences_array) > 0:
        rxionjob_sentence_array.append(rxion_sentences_array)
        return True

def OutputResults(job):
    print("\nHere's what we found for", job[0])
    print("-----------------------")
    # Prints all established variables for the input file.
    print("Software: ", job[1])
    print("Publisher: ", job[2])
    print("Information Webpage: ", job[3])
    print("Licensing Restrictions: ", job[4])
    print("-----------------------")

def HighlightText(usertext):    
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
rxion_array = []
rxionjob_sentence_array = [] #Temporary pattern matched sentence storage for jobs
jobDataArray = []
jobSentenceArray = []
jobSentencePatternArray = []
#sentences = []
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
        print("\nASEULA alpha v.1 for",current_sys)
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
        jobSentencePatternArray.append(rxionjob_sentence_array)
        i += 1

        # # Print document output
        # for job in jobSentenceArray:
        #     for element in job:
        #         print(element)

        # Print job output
        for job in jobDataArray:
            OutputResults(job)
        
        # Print runtime output
        # start = timeit.default_timer()
        end = timeit.default_timer()
        runtime = end - start
        if runtime > 59:
            print("Job runtime: " + str(runtime/60) + " Minutes\n")
        else:
            print("Job runtime: " + str(runtime) + " Seconds\n")

else:
    print("\nNo input was provided. Thank you for using ASEULA!\n")


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
    print(array_mode(entities))

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