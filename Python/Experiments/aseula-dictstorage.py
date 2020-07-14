# pip install spacy
# python -m spacy download en_core_web_sm
# pip install docx2txt
# pip install PyPDF2


import io
import os
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
tess.pytesseract.tesseract_cmd = r'C:\Users\Socce\AppData\Local\Tesseract-OCR\tesseract.exe'
from PIL import Image as im


# Function that finds the mode of an array.
def array_mode(list): 
    return(mode(list))


# Function that removes duplicate elements in an array.
def remove_duplicate(array):
    array = list(dict.fromkeys(array))
    return array


# Function that returns array elements as string.
# def array_to_string(array):
#     array_string = ""
#     for element in array:
#         array_string += element
#     return array_string


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

def script_output():
    print("Here's what we found...")
    print("-----------------------")
    # Prints all established variables for the input file.
    print("Software: ", selected_dict["software name"])
    print("Publisher: ", selected_dict["org"])
    print("Information Webpage: ", selected_dict["url"])
    print("Licensing Restrictions: ", selected_dict["restrictions"])
    print("-----------------------")

def arrayFormatting(array):
    i=1
    for element in array:
        print (str(i) + ".", element)
        i+=1
    print ("\n")

def rxion_formatting(dictionary):
    new_rxion_array = []
    for key in dictionary:
        if key in rxion_array:
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
    info_check = str(input("Is the information above correct? (y/n)  ")).lower().strip()
    if info_check == "y":
        print ("Information will shortly pushed to SharePoint. Thank you for using ASEULA!")
    elif info_check == "n":
        print ("\n")
        print (*fields, sep= ", ")
        field_correction = input("\nWhich of the fields information needs to be corrected?  ").lower().strip()
        if field_correction == "restrictions":
            print ('\n')
            print ('-' * 10)
            new_rxion_array = rxion_formatting(sentence_dict)
            new_string_rxion_array = array_to_string(remove_duplicate(new_rxion_array))
            selected_dict[field_correction] = new_string_rxion_array
            script_output()
            return user_input()
        else:
            print ('-' * 10)
            incorrect_data = field_dict[field_correction]
            print (*incorrect_data, sep=", ")
            user_selection = input("\nwhich value is correct?  ")
            index_element = incorrect_data.index(user_selection)
            selected_dict[field_correction] = incorrect_data[index_element]
            script_output()
            return user_input()
    else:
        print('Invalid input. Please try again.')
        return user_input()

# Checks the input file's format, converts it if necessary, opens it, and initializes the Spacy loader for the specified file.
# Checks if the input file is .txt.
def File_Conversion(fileInput): 
    if fileInput.endswith('.txt'):
        # Opens the .txt file.
        open_file = open(fileInput).read()
        # Performs NLP on the .txt file.
        document = nlp(open_file)
        # Checks if the input file is .docx.
        return document
    elif fileInput.endswith('.docx'):
        # Converts the .docx file to plaintext.
        open_file = docx2txt.process(fileInput)
        # Performs NLP on the converted plaintext.
        document = nlp(open_file)
        # Checks if the input file is .pdf.
        return document
    elif fileInput.endswith('.pdf'):
        # Saves the filename to a variable and establishes image resolution.
        pdf = wi(filename = fileInput, resolution = 400)
        # Converts pdf to jpeg.
        pdfImg = pdf.convert('jpeg')
        # Establishes a variable to hold JPEG text.
        open_file = ""
        # Loops through each image (one image per page) for the input PDF document.
        for img in pdfImg.sequence:
            # 
            page = wi(image = img)
            # Opens image.
            pic = im.open(io.BytesIO(page.make_blob('jpeg')))
            # Performs text recognition on the open image.
            text = tess.image_to_string(pic, lang = 'eng')
            # Appends text from image to open_file string.
            open_file += text
        # Removes line breaks from the file to aid sentence recognition.
        stripped_open_file = open_file.replace('\n', '')
        f = open("out.txt", "a")
        f.write(stripped_open_file)
        f.close()
        f = open("out2.txt", "a")
        f.write(open_file)
        f.close()
        # Performs NLP on complete open_file string.
        document = nlp(stripped_open_file)
        return document
        # # Opens the .pdf file.
        # open_file = open(stripped_filename,"rb")
        # # Establishes a variable for the .pdf read function.
        # pdf_parser = PyPDF2.PdfFileReader(open_file)
        # # Establishes a variable to save text parsed from the .pdf file.
        # pdf_plain_txt = ""
        # # Establishes loop to parse each page in the .pdf file.
        # for i in range(0,pdf_parser.numPages):
        #     # Appends parsed text page by page to the pdf_plain_txt variable.
        #     pdf_plain_txt += (pdf_parser.getPage(i).extractText().strip("\n"))
        # # Performs NLP on the variable (storing the extracted text from the .pdf file).
        # stripped_pdf_plain_txt = pdf_plain_txt.replace('\n', '')
        # f = open("out.txt", "a")
        # f.write(stripped_pdf_plain_txt)
        # f.close()
        # f = open("out2.txt", "a")
        # f.write(pdf_plain_txt)
        # f.close()
        # document = nlp(stripped_pdf_plain_txt)
    else:
        # Prints an error message if the input file does not match one of the supported formats.
        print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")


# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_sm')


# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))


# Accepts a file path as user input and strips it of quotation marks.
filename = input("Please enter the absolute path for the file you would like to process. ")
stripped_filename = filename.strip('"')
nlp_document = File_Conversion(stripped_filename)

###############################################    Organization     ###################################################

# Establishes variable to store matching entities.
organization_entity_array = []
# Establishes a variable to hold search patterns.
publisher_patterns = ["Inc", "Inc.", "Incorporated", "©", "Copyright"]
# Iterates through each entity in the input file.
for entity in nlp_document.ents:
    # Checks if entities in input file have the ORG label.
    if entity.label_ == "ORG" and any(pattern in entity.text for pattern in publisher_patterns):
        # Appends all entities with ORG label that contain any elements from the publisher_patterns array to the organization_entiity_array array.
        organization_entity_array.append(entity.text)
# Checks if organization_entity_array is empty. Prints mode of the array if elements exist.
if organization_entity_array:
    # Sets publisher_name as the mode of organization_entity_array.
    publisher_name = array_mode(organization_entity_array)
    publisher_name = publisher_name.replace('\n', ' ')
else:
    # Sets publisher_name as "Unknown."
    publisher_name = "Unknown"
org_findings = remove_duplicate(organization_entity_array)

###############################################    Software Name    ###################################################

# Establishes variable to store matching entities.
person_entity_string = ""
# Iterates through each entity in the input file.
for entity in nlp_document.ents:
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

###############################################    URL    #############################################################

# Extracts each word within the input file as an array. Space characters used as a delimiter.
token_split = nlp_document.text.split(" ")
# Establiishes an empty array to hold all possible URL matches.
url_array = []
# Iterates through each item in the token_split array.
for item in token_split:
    # Strips parentheses from each array item.
    stripped_item = item.strip('()')
    # Establishes a pattern to verify valid URLs.
    regex = re.compile('(https?://?\S+)')
# Checks if any items in the token_split array match the regular expression (regex variable). If so, the list item is appended to the url_array array.
    if re.match(regex, stripped_item):
        url_array.append(stripped_item)
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

###############################################    Restrictions    ####################################################

# Establishes variables to store restriction patterns and trigger words.
pos_trigger_words = ["only"]
neg_trigger_words = ["may not", "not permitted", "not allowed", "forbidden", "restricts", "restricted", "prohibits", "prohibited"]
rxion_instructional_patterns = ["teaching", "teaching use", "teaching-use", "instructional use", "instructional-use", \
"academic use", "academic-use", "academic instruction", "academic institution", "educational instruction", "educational institution"]
rxion_research_patterns = ["research", "research use", "research-use"]
rxion_physical_patterns = []
rxion_rdp_patterns = ["remote access", "remote-access", "remote desktop"]
rxion_campus_patterns = []
rxion_radius_patterns = []
rxion_us_patterns = []
rxion_vpn_patterns = []
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

# 
rxion_array = []
for sentence in nlp_document.sents:
    sentence_string = str(sentence) 
    sentence_lower = sentence_string.lower()
    if any(pattern in sentence_lower for pattern in rxion_instructional_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("Instructional-use only")
            rxion_instructional_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_research_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("Research-use only")
            rxion_research_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_physical_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):        
            rxion_array.append("Requires Physical Device")
            rxion_physical_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_rdp_patterns):
        if any(pattern in sentence_lower for pattern in neg_trigger_words):
            rxion_array.append("No RDP use")
            rxion_rdp_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_campus_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):        
            rxion_array.append("Use geographically limited (Campus)")
            rxion_campus_sentences.append(sentence)        
    if any(pattern in sentence_lower for pattern in rxion_radius_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("Use geographically limited (radius)")
            rxion_radius_sentences.append(sentence)            
    if any(pattern in sentence_lower for pattern in rxion_us_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("US use only")
            rxion_us_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_vpn_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("VPN required off-site")
            rxion_vpn_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_embargo_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("Block embargoed countries")
            rxion_embargo_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_poc_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("Block use from Persons of Concern")
            rxion_poc_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_lab_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("On-site (lab) use only")
            rxion_lab_sentences.append(sentence)
    if any(pattern in sentence_lower for pattern in rxion_site_patterns):
        if any(pattern in sentence_lower for pattern in pos_trigger_words):
            rxion_array.append("On-site use for on-site students only")
            rxion_site_sentences.append(sentence)
if not rxion_array:
    rxion_array.append("Needs Review")


string_rxion_array = array_to_string(remove_duplicate(rxion_array))

###############################################    Ask User    ########################################################
fields = ["Url", "Software name", "Organization", "Restricitons"]
selected_dict = {"url": information_webpage , "software name": software_name, "org": publisher_name, "restrictions": string_rxion_array}
field_dict = {"url": url_findings, "software name": software_findings, "org": org_findings}
sentence_dict = {"Instructional-use only": rxion_instructional_sentences,"Research-use only": rxion_research_sentences,"Requires Physical Device": rxion_physical_sentences, \
    "No RDP use": rxion_rdp_sentences,"Use geographically limited (Campus)": rxion_campus_sentences,"Use geographically limited (radius)": rxion_radius_sentences, \
    "US use only": rxion_us_sentences,"VPN required off-site": rxion_vpn_sentences,"Block embargoed countries": rxion_embargo_sentences, \
    "Block use from Persons of Concern": rxion_poc_sentences,"On-site (lab) use only": rxion_lab_sentences,"On-site use for on-site students only": rxion_site_sentences}
###############################################    Results    #########################################################

script_output()
user_input()

# counter = 0
# for sentence in nlp_document.sents:
#     counter+=1
# print("Counter: ", counter)



# instructional use only 
# ------------------
# sentences
# --------------
# do the displayed sentences match the restriction y/n 

# if yes go to next restricion if no remove restriction from clean_rxion_array 