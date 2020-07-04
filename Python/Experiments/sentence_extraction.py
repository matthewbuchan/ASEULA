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
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#Linux
#tess.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
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
    # ocr_input = ocr_input.read()
    all_paragraphs = re.split('\n{2,}', ocr_input)
    parsed_paragraphs = ""
    for paragraph in all_paragraphs:
        paragraph = paragraph.replace("\n", " ")
        parsed_paragraphs += str(paragraph) + "\n"
    return parsed_paragraphs

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
#nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('en_core_web_lg')


# Establishes variable for English sentence parsing method.
sentence_parser = English()
sentence_parser.add_pipe(sentence_parser.create_pipe('sentencizer'))

# ******************* TEST CODE *********************************

import timeit
start = timeit.default_timer()

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
    document = nlp(open_file)
# Checks if the input file is .docx.
elif stripped_filename.endswith('.docx'):
    # Converts the .docx file to plaintext.
    open_file = docx2txt.process(stripped_filename)
    # Performs NLP on the converted plaintext.
    document = nlp(open_file)
# Checks if the input file is .pdf.
elif stripped_filename.endswith('.pdf'):
    
    # #INPUT TRY
    # #PyPDF2 analysys
    # # Opens the .pdf file.
    # f_pypdf = open("./f_pypdf.txt","w+")
    # open_file = open(stripped_filename,"rb")
    # # Establishes a variable for the .pdf read function.
    # pdf_parser = PyPDF2.PdfFileReader(open_file)
    # # Establishes a variable to save text parsed from the .pdf file.
    # pdf_plain_txt_PyPDF = ""
    # # Establishes loop to parse each page in the .pdf file.
    # for i in range(0,pdf_parser.numPages):
    #     # Appends parsed text page by page to the pdf_plain_txt variable.
    #     pdf_plain_txt_PyPDF += (pdf_parser.getPage(i).extractText().strip("\n"))
    #     #pdf_plain_txt += (pdf_parser.getPage(i).extractText().strip("\n"))

    # # Performs NLP on the variable (storing the extracted text from the .pdf file).    
    # #document = nlp(pdf_plain_txt)
    # f_pypdf.write(str(open_file))
    # f_pypdf.close()
    # doc_PyPDF = nlp(pdf_plain_txt_PyPDF)
    
    #INPUT EXCEPT
    # # Saves the filename to a variable and establishes image resolution.
    pdf = wi(filename = stripped_filename, resolution = 300)
    # Converts pdf to jpeg.
    pdfImg = pdf.convert('jpeg')
    # Establishes a variable to hold JPEG text.
    pdf_plain_txt = ""
    #open_file = ""
    # Loops through each image (one image per page) for the input PDF document.
    f_pytess = open("./ocr_output.txt","w+")
    for img in pdfImg.sequence:
        page = wi(image = img)
        # Opens image.
        pic = im.open(io.BytesIO(page.make_blob('jpeg')))
        # Performs text recognition on the open image.
        text = tess.image_to_string(pic, lang = 'eng').strip("\n")
        # Appends text from image to open_file string.        
        pdf_plain_txt += text
        #open_file += text
    f_pytess.write(str(pdf_plain_txt))
    f_pytess.close()
    doc_Tess = nlp(pdf_plain_txt)
    doc_parsed = nlp(paragraph_parse(pdf_plain_txt))
    #doc_parsedlower = nlp(paragraph_parse_lower(pdf_plain_txt))

else:
    # Prints an error message if the input file does not match one of the supported formats.
    print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")




# #Sentence segmentation and output to file
# f_sent = open("./PyPDF_Sent.txt","w+")
# restrictions = ["academic", "research"]
# sent_cnt = 0
# for sent in doc_PyPDF.sents:
#     #print(sent)
#     f_sent.write("#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n")
#     sent_cnt += 1
# print("PyPDF2 Sentences: " + str(sent_cnt))


#Sentence segmentation and output to file
f_sent = open("./Sent_Tess.txt","w+")
sent_cnt = 0
text_temp = ""
for sent in doc_Tess.sents:
    #print(sent)
    text_temp += "#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n"
    #f_sent.write("#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n")
    sent_cnt += 1
f_sent.write("Tesseract sentence count: " + str(sent_cnt) + "\n\n" + str(text_temp))
print("Tesseract Sentences: " + str(sent_cnt))
f_sent.close()

# Paragraph separation
f_sent = open("./Sent_Parsed.txt","w+")

sent_cnt = 0
text_temp = ""
for sent in doc_parsed.sents:
    #print(sent)
    text_temp += "#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n"
    #f_sent.write("#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n")
    sent_cnt += 1

print("Parsed Sentences: " + str(sent_cnt))
f_sent.write("Parsed sentence count: " + str(sent_cnt) + "\n\n" + str(text_temp))
f_sent.close()



# # Paragraph separation with lower
# f_sent = open("./Sent_Parsed_Lower.txt","w+")
# restrictions = ["academic", "research"]
# sent_cnt = 0
# for sent in doc_parsedlower.sents:
#     #print(sent)
#     f_sent.write("#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n")
#     sent_cnt += 1
# print("Parsed Lower Sentences: " + str(sent_cnt))