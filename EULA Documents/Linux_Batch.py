import os

# Accepts a file path as user input and strips it of quotation marks.

filelist = os.system("ls -la *.pdf *.txt *.docx | awk '{print \"\\\"\"$9" "$10\"\\\"\"}' > newfile.txt")
f_list = ""
listfile = open("newfile.txt")
for line in listfile:    
    f_list = f_list +"./"+ line.strip('\"\n') + " "
os.system("python3 ../Python/Experiments/Testcoding.py " + f_list)
