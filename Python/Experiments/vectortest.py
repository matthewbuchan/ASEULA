# #Vector Check Function
# def vector_check(sentence):
#     patterns = ["teaching", "only" , "instructional", "academic","research", "remote access"]

#     restriction_token = ""
#     for element in patterns:    
#         restriction_token = nlp(element)
    
#         doc_token = nlp(sentence)
#         for token in restriction_token:
#             sent_output = ""
#             sent_inc = 0
#             #print(token.text, token.has_vector, token.vector_norm, token.is_oov)
#             for token1 in doc_token:
#                 token_sim = token.similarity(token1)
#                 if token_sim > .60:
#                     sent_output += " **" + str(token1) + "**"
#                     #print(token.text, token1.text, str(token.similarity(token1) * 100) + "% Similar")
#                     sent_inc += 1
#                 else:
#                     sent_output += " " + str(token1)
#         if sent_inc > 0:
#             #print(sent_output)
#             continue

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


# /// Packages to install \\\
# pip install spacy
# python -m spacy download en_core_web_sm
# pip install docx2txt
# pip install PyPDF2


import io
import os
import sys
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
# #Windows
# tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#Linux
tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
from PIL import Image as im

# Paragraph separation and fix
# def paragraph_parse_lower(ocr_input):
#     # ocr_input = ocr_input.read()
#     all_paragraphs = re.split('\n{2,}', ocr_input)
#     parsed_paragraphs = ""
#     for paragraph in all_paragraphs:
#         paragraph = paragraph.replace("\n", " ")
#         parsed_paragraphs += str(paragraph).lower() + "\n"
#     return parsed_paragraphs

def paragraph_parse(ocr_input):    
    all_paragraphs = re.split('\n{2,}', ocr_input)
    parsed_paragraphs = ""
    for paragraph in all_paragraphs:
        paragraph = paragraph.replace("\n", " ")
        parsed_paragraphs += str(paragraph) + "\n"
    return parsed_paragraphs

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

#Vector Check Function
def vector_check(sentence):
    patterns = ["teaching", "only" , "instructional", "academic","research", "remote access"]

    restriction_token = ""
    for element in patterns:    
        restriction_token = nlp(element)
    
        doc_token = nlp(sentence)
        for token in restriction_token:
            sent_output = ""
            sent_inc = 0
            #print(token.text, token.has_vector, token.vector_norm, token.is_oov)
            for token1 in doc_token:
                token_sim = token.similarity(token1)
                if token_sim > .60:
                    sent_output += " **" + str(token1) + "**"
                    #print(token.text, token1.text, str(token.similarity(token1) * 100) + "% Similar")
                    sent_inc += 1
                else:
                    sent_output += " " + str(token1)
        if sent_inc > 0:
            #print(sent_output)
            continue

def remove_stop_words(sentence):
    filtered_sentence = ""
    for token in sentence:
        if token.is_stop == False:
            filtered_sentence += " " + str(token.text)
    return filtered_sentence



# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
nlp = spacy.load('en_core_web_lg')


# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))

# ******************* TEST CODE *********************************

# Accepts a file path as user input and strips it of quotation marks.
#Argument input for batch processing
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:    
    filename = input("Please enter the absolute path for the file you would like to process. ")

import timeit
start = timeit.default_timer()
#stripped_filename = '\\\\192.168.100.60\\ASEULA_Share\\ASEULA\\Python\\SynopsysBetter.pdf'
stripped_filename = filename.strip('"')

# Checks the input file's format, converts it if necessary, opens it, and initializes the Spacy loader for the specified file.
# Checks if the input file is .txt.
if stripped_filename.endswith('.txt'):
    # Opens the .txt file.
    open_file = open(stripped_filename).read()
    # Performs NLP on the .txt file.
    document = open_file
# Checks if the input file is .docx.
elif stripped_filename.endswith('.docx'):
    # Converts the .docx file to plaintext.
    open_file = docx2txt.process(stripped_filename)
    # Performs NLP on the converted plaintext.
    document = open_file
# Checks if the input file is .pdf.
elif stripped_filename.endswith('.pdf'):



    # #LINUX OS command line conversion
    # os.system("convert -density 300 " + stripped_filename + " -depth 8 -strip -background white -alpha off tempimage.tiff")
    # os.system("tesseract tempimage.tiff extracted_text")
    # f = open("./extracted_text.txt").read()
    # document = nlp(paragraph_parse(f))
    # os.system("rm ./tempimage.tiff")


    # # Saves the filename to a variable and establishes image resolution.
    pdf = wi(filename = stripped_filename, resolution = 300)
    # Converts pdf to jpeg.
    pdfImg = pdf.convert('jpeg')
    # Establishes a variable to hold JPEG text.    
    open_file = ""
    # Loops through each image (one image per page) for the input PDF document.
    for img in pdfImg.sequence:
        page = wi(image = img)
        # Opens image.
        pic = im.open(io.BytesIO(page.make_blob('jpeg')))
        # Performs text recognition on the open image.
        text = tess.image_to_string(pic, lang = 'eng')
        # Appends text from image to open_file string.        
        open_file += text
        document = open_file

#Remove stop words

#     # Performs NLP on complete open_file string.
    #document = nlp(open_file)
    #document = nlp(paragraph_parse(open_file))



else:
    # Prints an error message if the input file does not match one of the supported formats.
    print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")



#Break into sentence array and store for analyzing.
document = nlp(paragraph_parse(document))
sentences = []
for sent in document.sents:
    sentences.append(sent) # Append sentences in array for future comparison

#Sentence Array NLP document creation
sent_count = 1
for sentence in sentences:    
    doc = nlp(str(sentence))




    # #Similarity check and sentence output
    # rxsion = nlp("teaching research academic instruction remote")
    # rx_sim = 0
    # for token in doc:
    #     for rx in rxsion:
    #         if rx.similarity(token) > .70:
    #             rx_sim = 1
    #             sent_count += 1
    # if rx_sim == 1:
    #     print(str(sent_count) + ". " + str(sentence))

    # #Part of Speech Tagging
    # for token in doc:
    #     print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{15}}')
    # sent_count += 1

    # #Purge Stop Words
    # purge_string = ""
    # for token in doc:
    #     if token.is_stop == 'False':
    #         purge_string += str(token.text) + " "
    #     else:
    #         continue

    # #Lemmatization
    # lemma_string = ""
    # for token in doc:
    #     purge_string += str(token.lemma_) + " "

    # #Syntactic dependency
    # for chunk in doc.noun_chunks:
    #     print(f'{chunk.text:{30}}{chunk.root.text:{15}}{chunk.root.dep_}')

    # #Output all token info
    # for token in doc:
    #     print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{10}} {token.is_stop}')

    #Named entity recognition ORG select
    ent_cnt = 0
    entities = {}
    for ent in doc.ents:
        #FIND Company    
        if ent.label_.lower() == "org":
            entities['ent.text.title()'] += 1
            print(entities['ent.text.title()'])
    print(entities)
    software_company = ""
    for token in doc:
        if token.text.capitalize() in entities:        
            if token.pos_ == "PROPN" and token.dep_ == "pobj":
                print("YOUR COMPANY NAME IS: " + str(token.text.capitalize()))
        print(f'{token.text:{15}} {token.lemma_:{15}} {token.pos_:{10}} {token.dep_:{15}}')
        ent_cnt += 1
    print("Company = " + str(software_company))
    print("Total Entities = " + str(ent_cnt))


#Process runtime output
end = timeit.default_timer()
runtime = end - start
if runtime > 59:
    print("Job runtime: " + str(runtime/60) + " Minutes")
else:
    print("Job runtime: " + str(runtime) + " Seconds")

# # # # Displacy output to browser
# from spacy import displacy
# #Obtain IP for browser view
# import socket
# host_ip = socket.gethostbyname(socket.gethostname())
# print("\nYour rendered strings will be located at the following address: "+ str(host_ip) + ":5000\n")
# i = 1
# for sentence in sentences:
#     print("Sentence " + str(i) + " of " + str(len(sentences)))
#     displacy.serve(sentence, style='dep')
#     input()