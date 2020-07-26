########################################################  IMPORT/INSTALL  ########################################################

# pip install spacy
# python -m spacy download en_core_web_sm
# pip install docx2txt
# pip install PyPDF2
# pip install pytesseract
# pip install wand
# pip install tqdm
# pip install colored
# pip install colorama

import io, os, sys, re, timeit, statistics, docx2txt, PyPDF2, re, spacy, pytesseract as tess, platform
from spacy.lang.en import English
from re import search
from statistics import mode
from wand.image import Image as wi
from tqdm import tqdm # Progress Bar
from colored import fg, bg, attr # Highlighted Text
from colorama import Fore, Back, Style # Highlighted Text
from PIL import Image as im

########################################################  SCRIPT CONFIG  ########################################################

current_sys = platform.system()
if current_sys.lower() == "windows":
    if os.path.isfile(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # WINDOWS DEFAULT INSTALL
    elif os.path.isfile(r'C:\Users\Socce\AppData\Local\Tesseract-OCR\tesseract.exe'):
        tess.pytesseract.tesseract_cmd = r'C:\Users\Socce\AppData\Local\Tesseract-OCR\tesseract.exe' # WINDOWS USER INSTALL
    else:
        tess.pytesseract.tesseract_cmd = input("Please enter the path for tesseract.exe: ")
elif current_sys.lower() == "linux":
    tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' #LINUX

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_sm')

# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))

########################################################    FUNCTIONS    ########################################################

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
    # Checks the input file's format, converts it if necessary, opens it, and initializes the Spacy loader for the specified file.
    # Checks if the input file is .txt.
    if inputfilename.endswith('.txt'):
        # Opens the .txt file.
        try:
            open_file = open(inputfilename).read()
        except:
            open_file = ConvertAnsi(inputfilename)
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

def ParagraphParse(ocr_input):    
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

def ASEULA_Function(document,full_job_text):

    #------------------------------------------------  PUBLISHER NAME  ------------------------------------------------#

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
                        organization_entity_array.append(str(entity.text).title())
        

        # Appends all entities with ORG label that contain any elements from the publisher_patterns array to the organization_entiity_array array.
        
        # #SEARCH STRING FOR ENTITIES
        # if "org" in entity.label_.lower():
        # if "autodesk" in entity.text.lower():
        #     print(f'{entity.text:{30}} {entity.label_:{30}} ')
        # print(f'{entity.text.title():{30}} {entity.label_:{30}} ')
                    
    # Checks if organization_entity_array is empty. Prints mode of the array if elements exist.
    if organization_entity_array:
        # Sets publisher_name as the mode of organization_entity_array.
        try:
            publisher_name = ArrayMode(organization_entity_array)
            publisher_name = publisher_name.replace('\n', ' ')
        except:
            publisher_name = "Unknown"
    else:
        # Sets publisher_name as "Unknown."
        publisher_name = "Unknown"
    org_findings = RemoveDuplicate(organization_entity_array)

    #------------------------------------------------  SOFTWARE NAME  ------------------------------------------------#
    
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
    clean_propn_token_array = RemoveDuplicate(propn_token_array)
    matching = [item for item in clean_propn_token_array if item in publisher_name]
    # Removes any duplicate array elements from matching.
    stripped_matching = RemoveDuplicate(matching)
    if matching:
        # Sets software_name as the string for the stripped_matching array.
        software_name = ArrayToString(stripped_matching)
    elif not matching:
        # Sets software_name as the mode of propn_token_array.
        try:
            software_name = ArrayMode(propn_token_array)
        except:
            software_name = "Unknown"
    else:
        # Sets software_name as "Unknown."
        software_name = "Unknown"
    software_findings = clean_propn_token_array + stripped_matching
    software_findings = RemoveDuplicate(software_findings)

    #------------------------------------------------  INFORMATION WEBPAGE  ------------------------------------------------#
   
    # Extracts each word within the input file as an array. Space characters used as a delimiter.
    url_array = URLList(sentences) # FORCE URL FUNCTION FILL instead of regex

    # Checks if url_array is empty. Prints mode of the array if elements exist.
    if url_array:
        # Sets information_webpage as the mode of url_array.
        information_webpage = ArrayMode(url_array)
        # Removes any line breaks in the extracted URL.
        information_webpage = information_webpage.replace('\n', '')
    else:
        # Sets information_webpage as "Unknown."
        information_webpage = "Unknown"
    url_findings = RemoveDuplicate(url_array)

    #------------------------------------------------  RESTRICTIONS  ------------------------------------------------#

    # Establishes variables to store restriction patterns and trigger words.
    rxion_array = []
    rxion_patterns = {}
    pos_trigger_words = ["only","grant","allow","permit","granting"]
    neg_trigger_words = ["no","not","may not", "not permitted", "not allowed", "forbidden", "restricts", "restricted", "prohibits", "prohibited"]
    rxion_patterns["Instructional-use only"] = ["teaching", "instruction","academic","purposes", "educational","institution"]
    rxion_patterns["Research-use only"] = ["research"]
    rxion_patterns["Requires Physical Device"] = ["activation key"]
    rxion_patterns["No RDP use"] = ["remote access", "remote", "rdp", "remote interface"]
    rxion_patterns["Use geographically limited (Campus)"] = ["internally","designated site", "customer's campus"]
    rxion_patterns["Use geographically limited (radius)"] = ["radius", "geographically-limited radius", "particular geography", "site license"]
    rxion_patterns["US use only"] = ["united states use", "u.s.", "u.s. use","export"]
    rxion_patterns["VPN required off-site"] = ["vpn", "virtual private network"]
    rxion_patterns["Block embargoed countries"] = ["embargo", "embargoed", "embargoed country","export"]
    rxion_patterns["Block use from Persons of Concern"] = ["person of concern", "persons of concern", "people of concern","denied persons"]
    rxion_patterns["On-site (lab) use only"] = ["lab-use"]
    rxion_patterns["On-site use for on-site students only"] = ["fixed geographic site", "geographic site", "on-site", "on-site use"]
    rxion_patterns["Virtualization Allowed"] = ["virtualization", "virtualizing", "multiplexing", "pooling"]
    restriction_sentence_dict = dict()
        
    # Restriction runs
    for rxion in rxion_patterns:
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
    for sent in document.sents:
        sentence = str(sent).lower()
        for rx in rx_array:
            if rx[2] in sentence:
                if any(pattern in restrictionString.lower() for pattern in neg):
                    if rx[0] in sentence and str(sent) not in rxion_sentences_array:
                        rxion_sentences_array.append(str(sent))
                    elif rx[0] not in sentence and str(sent) not in rxion_sentences_array:
                        rxion_sentences_array.append(str(sent))
                elif rx[0] in sentence and str(sent) not in rxion_sentences_array:                    
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

def RxionSentenceOutput(dictionary):
    new_rxion_array = []
    for key in dictionary:
        if key in job[4]:
            print (key)
            print("-----------------------")
            # # Added loop to print entire document with flagged text highlighted.
            # doctext = str(job[10])
            # for element in dictionary[key]:
            #     doctext = re.sub(str(element),str(HighlightText(element)),doctext)
            # print(doctext)
            ArrayFormatting(dictionary[key])
            user_selection = input("\nIs this restriction flagged correctly? (y/n)  ").lower()
            if user_selection == "y":
                new_rxion_array.append(key)                
            elif user_selection == "n":
                print ("This restriction will be unflagged.\n")    
    return new_rxion_array

def ArrayFormatting(array):
    i=1
    for element in array:
        print (str(i) + ".", element)
        i+=1
    print ("\n")

def HighlightText(usertext):
    from colorama import Fore, Back, Style
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

def ParagraphToLower(inputtext):
    return inputtext.group(0).lower()

###############################################    EXECUTION    ###############################################

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
    print("\nASEULA Alpha V.1 for",current_sys)
    filename_array = []
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
    print("\nPlease wait while we process",len(filename_array),"file(s)... \n")
    for job in filename_array:
        text = ProcessInputFile(job)
        text = ParagraphParse(text)
        text = re.sub(r'\([A-z0-9]{1,3}?\)',"",text) # Remove (a), (b), (iii) bulleting.
        text = re.sub(r'\b[A-Z]{2,}\b',ParagraphToLower,text) # Change full uppercase paragraphs to lower.
        document = nlp(text)
        sentences = []
        for sent in document.sents:
            sentences.append(re.sub(r'\n{1,}'," ",str(sent))) # Remove new line characters from each sentence.
            #sentences.append(sent) # Append sentences in array for future comparison.
        full_job_text = ""
        for sentence in sentences:
            full_job_text = full_job_text + str(sentence) + "\n"
        jobDataArray.append(ASEULA_Function(document,full_job_text))
        i += 1
else:
    print("\nNo input was provided. Thank you for using ASEULA!\n")

#Processing time output
end = timeit.default_timer()
runtime = end - start
if runtime > 59:
    print("\nJob Runtime: " + str(runtime/60) + " Minutes\n")
else:
    print("\nJob Runtime: " + str(runtime) + " Seconds\n")
    
for job in jobDataArray:
    OutputResults(job)

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