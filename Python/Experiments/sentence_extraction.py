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

# Load English tokenizer, tagger, parser, named entity recognition (NER), and word vectors.
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
    
    #INPUT TRY
    #PyPDF2 analysys
    # Opens the .pdf file.
    open_file = open(stripped_filename,"rb")
    # Establishes a variable for the .pdf read function.
    pdf_parser = PyPDF2.PdfFileReader(open_file)
    # Establishes a variable to save text parsed from the .pdf file.
    pdf_plain_txt_PyPDF = ""
    # Establishes loop to parse each page in the .pdf file.
    for i in range(0,pdf_parser.numPages):
        # Appends parsed text page by page to the pdf_plain_txt variable.
        pdf_plain_txt_PyPDF += (pdf_parser.getPage(i).extractText().strip("\n"))
        #pdf_plain_txt += (pdf_parser.getPage(i).extractText().strip("\n"))
    # Performs NLP on the variable (storing the extracted text from the .pdf file).    
    #document = nlp(pdf_plain_txt)
    
    #INPUT EXCEPT
    # # Saves the filename to a variable and establishes image resolution.
    pdf = wi(filename = stripped_filename, resolution = 300)
    # Converts pdf to jpeg.
    pdfImg = pdf.convert('jpeg')
    # Establishes a variable to hold JPEG text.
    pdf_plain_txt = ""
    #open_file = ""
    # Loops through each image (one image per page) for the input PDF document.
    for img in pdfImg.sequence:
        page = wi(image = img)
        # Opens image.
        pic = im.open(io.BytesIO(page.make_blob('jpeg')))
        # Performs text recognition on the open image.
        text = tess.image_to_string(pic, lang = 'eng')
        # Appends text from image to open_file string.        
        pdf_plain_txt += text
        #open_file += text

    doc_PyPDF = nlp(pdf_plain_txt_PyPDF)
    doc_Tess = nlp(pdf_plain_txt)

else:
    # Prints an error message if the input file does not match one of the supported formats.
    print("Oops! Your file format is not supported. Please convert your file to .txt, .docx, or .pdf to continue.")


#Sentence segmentation and output to file
f_sent = open("./PyPDF_Sent.txt","w+")
restrictions = ["academic", "research"]
sent_cnt = 0
for sent in doc_PyPDF.sents:
    #print(sent)
    f_sent.write("#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n")
    sent_cnt += 1
print("PyPDF2 Sentences: " + str(sent_cnt))


#Sentence segmentation and output to file
f_sent = open("./Tess_Sent.txt","w+")
restrictions = ["academic", "research"]
sent_cnt = 0
for sent in doc_Tess.sents:
    #print(sent)
    f_sent.write("#" + str(sent_cnt) + " " + str(sent) + "\n--------------------------\n")
    sent_cnt += 1
print("Tesseract Sentences: " + str(sent_cnt))
