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
def ProcessInputFile(inputfilename): # Determines file type and conversion steps
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
def ConvertAnsi(file_input): # Converts .txt files if not formatted properly
    import codecs    
    inputfile = file_input    
    if current_sys.lower() == "windows":
        with io.open( inputfile , mode='r', encoding='utf8') as fc:
            content = fc.read()
        return content
    else:
        return inputfile
def ParagraphParse(ocr_input): # Splits paragraphs before processing occurs
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
def AseulaFunction(document,full_job_text): # Performs data extraction from the converted documents

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
        publisher_name = ArrayMode(organization_entity_array)
        publisher_name = publisher_name.replace('\n', ' ')
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
        software_name = ArrayMode(propn_token_array)
    else:
        # Sets software_name as "Unknown."
        software_name = "Unknown"
    software_findings = clean_propn_token_array + stripped_matching
    software_findings = RemoveDuplicate(software_findings)

    #------------------------------------------------  INFORMATION WEBPAGE  ------------------------------------------------#
   
    # Extracts each word within the input file as an array. Space characters used as a delimiter.
    url_array = UrlList(sentences) # FORCE URL FUNCTION FILL instead of regex

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
    pos_trigger_words = ["only", "grant", "grants", "granting", "granted", "allow", "allows", "allowing", "allowed", "permit", \
        "permits", "permitting", "permitted", "require", "requires", "requiring", "required", "authorize", "authorizes", \
            "authorizing", "authorized", "necessary"]
    neg_trigger_words = ["no", "not", "may not", "not granted", "not allowed", "not permitted", "forbidden", "restricts", "restricted",\
         "prohibits", "prohibited"]
    rxion_instructional_patterns = ["teaching", "teaching use", "teaching-use", "instruction", "instructional use",\
         "instructional-use", "instructional purposes", "academic", "academic use", "academic-use", "academic instruction",\
              "academic institution", "academic purposes", "educational", "educational use", "educational-use",\
                   "educational instruction", "educational institution", "institution", "educational purposes"]
    rxion_research_patterns = ["research", "research use", "research-use"]
    rxion_physical_patterns = ["activation key", "dongle"]
    rxion_rdp_patterns = ["remote", "rdp", "remote access", "remote-access", "remote desktop", "remote interface"]
    rxion_campus_patterns = ["designated site", "customer's campus", "internally"]
    rxion_radius_patterns = ["radius", "limited radius", "geographically limited radius",\
         "geographically-limited radius", "particular geography", "site license", "site licenses"]
    rxion_us_patterns = ["united states", "united states use", "u.s.", "u.s. use","export"]
    rxion_vpn_patterns = ["vpn", "virtual private network", "remote access"]
    rxion_embargo_patterns = ["embargo", "embargoed", "embargoed country","export"]
    rxion_poc_patterns = ["person of concern", "persons of concern", "people of concern",\
        "denied persons"]
    rxion_lab_patterns = ["lab-use"]
    rxion_site_patterns = ["single fixed geographic site", "fixed geographic site",\
         "geographic site", "on-site", "on-site use"]
    #rxion_virt_patterns = ["virtualization", "virtualizing", "multiplexing", "pooling"]

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
    for sentence in document.sents:
        sentence_string = str(sentence) 
        sentence_lower = sentence_string.lower()
        if any(pattern in sentence_lower for pattern in rxion_instructional_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Instructional-use only")
                rxion_instructional_sentences.append(HighlightText(sentence))
                # print(HighlightText(sentence_string))
            else:
                rxion_instructional_sentences.append(sentence)
        if any(pattern in sentence_lower for pattern in rxion_research_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Research-use only")
                rxion_research_sentences.append(HighlightText(sentence))
                # print(HighlightText(sentence_string))
            else:
                rxion_research_sentences.append(sentence)
        if any(pattern in sentence_lower for pattern in rxion_physical_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("Requires Physical Device")
                rxion_physical_sentences.append(HighlightText(sentence))
                # print(HighlightText(sentence_string))       
            else:
                rxion_physical_sentences.append(sentence)
        if any(pattern in sentence_lower for pattern in rxion_rdp_patterns):
            if any(pattern in sentence_lower for pattern in neg_trigger_words):
                rxion_array.append("No RDP use")
                rxion_rdp_sentences.append(HighlightText(sentence))
                # print(HighlightText(sentence_string))
            else:
                rxion_rdp_sentences.append(sentence)
        if any(pattern in sentence_lower for pattern in rxion_campus_patterns):
            rxion_array.append("Use geographically limited (Campus)")
            rxion_campus_sentences.append(sentence)  
            # print(HighlightText(sentence_string))

        if any(pattern in sentence_lower for pattern in rxion_radius_patterns):
            rxion_array.append("Use geographically limited (radius)")
            rxion_radius_sentences.append(sentence)
            # print(HighlightText(sentence_string))

        if any(pattern in sentence_lower for pattern in rxion_us_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("US use only")
                rxion_us_sentences.append(HighlightText(sentence))
                # print(HighlightText(sentence_string))
            else:
                rxion_us_sentences.append(sentence)
        if any(pattern in sentence_lower for pattern in rxion_vpn_patterns):
            if any(pattern in sentence_lower for pattern in pos_trigger_words):
                rxion_array.append("VPN required off-site")
                rxion_vpn_sentences.append(HighlightText(sentence))
                # print(HighlightText(sentence_string))
            else:
                rxion_vpn_sentences.append(sentence)
        if any(pattern in sentence_lower for pattern in rxion_embargo_patterns):
            rxion_array.append("Block embargoed countries")
            rxion_embargo_sentences.append(sentence)
            # print(HighlightText(sentence_string))
            
        if any(pattern in sentence_lower for pattern in rxion_poc_patterns):
            rxion_array.append("Block use from Persons of Concern")
            rxion_poc_sentences.append(sentence)
            # print(HighlightText(sentence_string))

        if any(pattern in sentence_lower for pattern in rxion_lab_patterns):
            rxion_array.append("On-site (lab) use only")
            rxion_lab_sentences.append(sentence)
            # print(HighlightText(sentence_string))

        if any(pattern in sentence_lower for pattern in rxion_site_patterns):
            rxion_array.append("On-site use for on-site students only")
            rxion_site_sentences.append(sentence)
            # print(HighlightText(sentence_string))

        # else:
        #     print(sentence_string)
    # i = 1
    # for element in rxion_sentence_array:
    #     print(rxion_array)
    #     print(i, " --- " ,element)
    #     i += 1

    if not rxion_array:        
        rxion_array.append("Needs Review")

    string_rxion_array = ArrayToString(RemoveDuplicate(rxion_array))

    fields = ["Software Name", "Publisher", "Information Webpage", "Licensing Restrictions"]
    selected_dict = {"software name": software_name, "publisher": publisher_name, "information webpage": information_webpage, "licensing restrictions": string_rxion_array}
    field_dict = {"software name": software_findings, "publisher": org_findings, "information webpage": url_findings}
    sentence_dict = {"Instructional-use only": rxion_instructional_sentences,"Research-use only": rxion_research_sentences,"Requires Physical Device": rxion_physical_sentences, \
        "No RDP use": rxion_rdp_sentences,"Use geographically limited (Campus)": rxion_campus_sentences,"Use geographically limited (radius)": rxion_radius_sentences, \
        "US use only": rxion_us_sentences,"VPN required off-site": rxion_vpn_sentences,"Block embargoed countries": rxion_embargo_sentences, \
        "Block use from Persons of Concern": rxion_poc_sentences,"On-site (lab) use only": rxion_lab_sentences,"On-site use for on-site students only": rxion_site_sentences}

    return [os.path.basename(job),software_name,publisher_name,information_webpage, rxion_array, string_rxion_array, fields, selected_dict, field_dict, sentence_dict, full_job_text]
def OutputResults(job): # Summarized output
    print("\nHere's what we found for", job[0])
    print("-----------------------")
    # Prints all established variables for the input file.
    print("Software: ", job[7]["software name"])
    print("Publisher: ", job[7]["publisher"])
    print("Information Webpage: ", job[7]["information webpage"])
    print("Licensing Restrictions: ", job[7]["licensing restrictions"])
    print("-----------------------")
    UserValidation()
def UserValidation(): # Provides interface for users to validate findings
    while True:
        info_check = str(input("Is the information above correct? (y/n)  ")).lower().strip()
        if info_check == "y":
            print ("\nInformation will be pushed to SharePoint shortly. Thank you for using ASEULA!")
            break
        elif info_check == "n":
            print("-----------------------")
            for selection in job[6]:
                print(str(job[6].index(selection) + 1) + ".",selection)
                #print (*job[6], sep= ", ")
            while True:
                field_correction = int(input("\nWe're sorry. Which of the following fields is incorrect? Please enter the corresponding number. "))
                if field_correction == 4:
                    print ('\n')
                    new_rxion_array = RxionSentenceOutput(job[9])
                    job[7][job[6][field_correction - 1].lower()] = ArrayToString(RemoveDuplicate(new_rxion_array)) #selected_dict[field_correction] = new_string_rxion_array
                    OutputResults(job)
                    break
                elif field_correction == 1 or field_correction == 2 or field_correction == 3:
                    print("-----------------------")
                    incorrect_data = job[8][job[6][field_correction - 1].lower()]
                    if incorrect_data:
                        for item in incorrect_data:
                            print(str(incorrect_data.index(item) + 1) + ".",item)
                        while True:
                            user_selection = input("\nWhich value is correct? If none are correct, please enter one. ")
                            try:
                                user_selection = int(user_selection)
                                if user_selection <= len(incorrect_data) + 1:
                                    job[7][job[6][field_correction - 1].lower()] = incorrect_data[user_selection - 1]
                                    break
                                else:
                                    print("Error! Invalid input. Please enter a valid number or string.")
                            except:
                                if type(user_selection) == str:
                                    job[8][job[6][field_correction - 1].lower()].append(user_selection)
                                    job[7][job[6][field_correction - 1].lower()] = user_selection
                                    print("\nAre you sure you want to use",user_selection,"?")                                
                                    break
                        OutputResults(job)
                        break
                    else:
                        user_selection = str(input("\nNo value were found, please provide the correct value if it is known. "))
                        job[8][job[6][field_correction - 1].lower()].append(user_selection)
                        job[7][job[6][field_correction - 1].lower()] = user_selection
                        OutputResults(job)
                        break
                else: 
                    print("Error! Invalid input. Please enter a valid field option.")
            break
        else:
            print('Invalid input. Please try again.')
def RxionSentenceOutput(dictionary): # Displays restriction sentences used in the UserValidation function
    new_rxion_array = []
    for key in dictionary:
        if dictionary[key] != []:
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
def ArrayFormatting(array): # Returns dictionary items requested by the RxionSentenceOutput
    i=1
    for element in array:
        print (str(i) + ".", element)
        i+=1
    print ("\n")
def HighlightText(usertext): # Returns inputted text as yellow for easy identification
    from colorama import Fore, Back, Style
    return Fore.YELLOW + str(usertext) + Fore.RESET
def ArrayMode(list): # Assists in determining entities from the ASEULAFunction
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
def ParagraphToLower(inputtext): # Changes full uppercase paragraphs to lower.
    return inputtext.group(0).lower()
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
    print("\nASEULA Alpha Build 200727 for",current_sys)
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
# Evaluates for inputted files and processes the files
if len(filename_array) > 0:
    start = timeit.default_timer()
    print("\nPlease wait while we process",len(filename_array),"file(s)... \n")
    for job in filename_array:
        text = ProcessInputFile(job)
        text = ParagraphParse(text)
        text = re.sub(r'\([A-z0-9]{1,3}?\)',"",text) # Remove (a), (b), (iii) bulleting.
        text = re.sub(r'\b[A-Z]{2,}\b',ParagraphToLower,text) 
        document = nlp(text)
        sentences = []
        for sent in document.sents:
            sentences.append(re.sub(r'\n{1,}'," ",str(sent))) # Remove new line characters from each sentence.            
        full_job_text = ""
        for sentence in sentences:
            full_job_text = full_job_text + str(sentence) + "\n"
        jobDataArray.append(AseulaFunction(document,full_job_text))
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