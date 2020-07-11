
import os

# Accepts a file path as user input and strips it of quotation marks.




filelist = os.system("ls -la *.pdf | awk '{print \"\\\"\"$9" "$10\"\\\"\"}' > newfile.txt")
listfile = open("newfile.txt")
for line in listfile:
    print("Processing " + line.strip("\n"))
    os.system("python3 aseula_Linux.py " + line.strip("\n"))
