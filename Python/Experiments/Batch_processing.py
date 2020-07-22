import os, platform

# Accepts a file path as user input and strips it of quotation marks.
current_sys = platform.system()
if current_sys.lower() == "windows":
    f_directory = "X:\ASEULA\EULA Documents"
    filelist = os.listdir(f_directory)
    f_args = ""
    for f in filelist:
        if ".pdf" in str(f) or ".docx" in str(f) or ".txt" in str(f):
            f_args +=" \"" + str(f_directory) + "\\" + str(f) + "\" "
    os.system("python X:\ASEULA\Python\Experiments\Testcoding.py " + str(f_args))
    
elif current_sys.lower() == "linux":
    filelist = os.system("ls -la *.pdf *.txt *.docx | awk '{print \"\\\"\"$9" "$10\"\\\"\"}' > newfile.txt")
    f_list = ""
    listfile = open("newfile.txt")
    for line in listfile:    
        f_list = f_list +"./"+ line.strip('\"\n') + " "
    os.system("python3 ../Python/Experiments/Testcoding-regex.py " + f_list)
