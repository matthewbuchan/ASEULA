# script specific to linux installation

# sudo apt install tesseract-ocr
# sudo apt install libtesseract-dev
# pip3 install spacy
# python3 -m spacy download en_core_web_lg
# pip3 install docx2txt
# pip3 install PyPDF2

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

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_lg')


# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))


# Accepts a file path as user input and strips it of quotation marks.
filename = input("Please enter the absolute path for the file you would like to process. ")
stripped_filename = filename.strip('"')


# Checks the input file's format, converts it if necessary, opens it, and initializes the Spacy loader for the specified file.
# Checks if the input file is .txt.
if stripped_filename.endswith('.txt'):
    # Opens the .txt file.
    open_file = open(stripped_filename).read()
    # Performs NLP on the .txt file.
    document = nlp(open_file)
# Checks if the input file is .docx.
elif stripped_filename.endswith('.docx'):
    # Converts the .docx file to plaintext.
    open_file = docx2txt.process(stripped_filename)
    # Performs NLP on the converted plaintext.
    document = nlp(open_file)
# Checks if the input file is .pdf.
elif stripped_filename.endswith('.pdf'):
    os.system("convert -density 300 " + filename + " -depth 8 -strip -background white -alpha off tempimage.tiff")
    os.system("tesseract tempimage.tiff extracted_text")
    f = open("./extracted_text.txt").read()
    document = nlp(f)

else:
    # Prints an error message if the input file does not match one of the supported formats.
    print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")


# Establishes variable to store matching entities.
organization_entity_array = []
# Establishes a variable to hold search patterns.
publisher_patterns = ["Inc", "Inc.", "Incorporated", "©", "Copyright"]
# Iterates through each entity in the input file.
for entity in document.ents:
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
    regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
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


# Establishes variables to store restriction patterns.
rxion_instructional_patterns = ["teaching use", "instructional use", "academic instruction", "teaching only"]
rxion_research_patterns = ["research only", "research use", "research use only"]
rxion_physical_patterns = []
rxion_rdp_patterns = ["remote access"]
rxion_campus_patterns = []
rxion_radius_patterns = []
rxion_us_patterns = []
rxion_vpn_patterns = []
rxion_embargo_patterns = []
rxion_poc_patterns = []
rxion_lab_patterns = []
rxion_site_patterns = []

# 
rxion_array = []
rxion_sentence_array = []
for sentence in document.sents:
    sentence_string = str(sentence)
    if any(pattern in sentence_string for pattern in rxion_instructional_patterns):
        rxion_array.append("Instructional-use only")
    if any(pattern in sentence_string for pattern in rxion_research_patterns):
        rxion_array.append("Research-use only")
    if any(pattern in sentence_string for pattern in rxion_physical_patterns):
        rxion_array.append("Requires Physical Device")
    if any(pattern in sentence_string for pattern in rxion_rdp_patterns):
        rxion_array.append("No RDP use")
    if any(pattern in sentence_string for pattern in rxion_campus_patterns):
        rxion_array.append("Use geographically limited (Campus)")
    if any(pattern in sentence_string for pattern in rxion_radius_patterns):
        rxion_array.append("Use geographically limited (radius)")
    if any(pattern in sentence_string for pattern in rxion_us_patterns):
        rxion_array.append("US use only")
    if any(pattern in sentence_string for pattern in rxion_vpn_patterns):
        rxion_array.append("VPN required off-site")
    if any(pattern in sentence_string for pattern in rxion_embargo_patterns):
        rxion_array.append("Block embargoed countries")
    if any(pattern in sentence_string for pattern in rxion_poc_patterns):
        rxion_array.append("Block use from Persons of Concern")
    if any(pattern in sentence_string for pattern in rxion_lab_patterns):
        rxion_array.append("On-site (lab) use only")
    if any(pattern in sentence_string for pattern in rxion_site_patterns):
        rxion_array.append("On-site use for on-site students only")
if not rxion_array:
    rxion_array.append("Needs Review")


string_rxion_array = array_to_string(remove_duplicate(rxion_array))


print("Here's what we found...")
print("-----------------------")
# Prints all establishes variables for the input file.
print("Software: ", software_name)
print("Publisher: ", publisher_name)
print("Information Webpage: ", information_webpage)
print("Licensing Restrictions: ", string_rxion_array)


# Version
# Licensing Restrictions


# Instructional Use Only
# Research Use Only
# Requires Physical Device
# No RDP use

# Use geographically limited (Campus)
# Use geographically limited (radius) 
# US use only
# VPN required off-site

# Block embargoed countries
# Block use from Persons of Concern
# On-site (lab) use only
# On-site use for on-site students only

# None
# Needs Review
