import os
import sys
from threading import Thread
import time
import pyautogui

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def printLoading(condition, suffix = ''):
    animation = [
        "[        ]",
        "[=       ]",
        "[===     ]",
        "[====    ]",
        "[=====   ]",
        "[======  ]",
        "[======= ]",
        "[========]",
        "[ =======]",
        "[  ======]",
        "[   =====]",
        "[    ====]",
        "[     ===]",
        "[      ==]",
        "[       =]",
        "[        ]",
        "[        ]"
    ]
    i = 0
    while condition():
        print(animation[i % len(animation)] + " " + suffix, end='\r')
        time.sleep(.1)
        i += 1

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Configuration
print("FL Studio Project Exporter by marian (: Enjoy!")
print("---------------------------------------------")
folderName = input("Enter folder path (search is recursive!): ")
allowOverwrite = True if input("Allow overwrite? (y/n): ") == "y" else False
deleteAudiosAfterExporting = True if input("Delete audio files after exporting the project? (y/n): ") == "y" else False

os.system('cls' if os.name == 'nt' else 'clear') # Clear terminal
project_count = -1

def count_files_recursively(directory):
    count = 0
    for file in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, file)):
            count += count_files(os.path.join(directory, file))
        elif file.endswith(".flp"):
            count += 1
    return count

try:
    directory = os.fsdecode(folderName)

    def count_files():
        time.sleep(5)
        global project_count
        project_count = count_files_recursively(directory)
    Thread(target = count_files).start()
    
    def check_initialized():
        return project_count == -1
    printLoading(check_initialized, "Initializing...")
except FileNotFoundError:
    sys.exit("Folder not found")

def recursive_save(directory):
    for file in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, file)):
            recursive_save(os.path.join(directory, file))
        else:
            filename = os.fsdecode(file)
            if filename.endswith(".flp"):
                save_project(os.path.join(directory, filename))

def fl_project_contains_problems():
    try:
        pyautogui.locateOnScreen(resource_path('images/fl-studio-loading-problems.png'), grayscale=True, confidence=0.8)
        return True
    except:
        return False
    
def fl_processing_zip():
    try:
        pyautogui.locateOnScreen(resource_path('images/fl-studio-processing-zip.png'), grayscale=True, confidence=0.8)
        return True
    except:
        return False

def has_overwrite_problem():
    try:
        pyautogui.locateOnScreen(resource_path('images/win-overwrite-error.png'), grayscale=True, confidence=0.8)
        return True
    except:
        return False

projects_saved = 0

def save_project(path):   
    global projects_saved
    printProgressBar(projects_saved, project_count, prefix = 'Progress:', suffix = path, length = 50)

    fileTabLocation = pyautogui.locateOnScreen(resource_path('images/fl-studio-file-tab.png'), grayscale=True, confidence=0.8)
    pyautogui.click(fileTabLocation)

    openButton = pyautogui.locateOnScreen(resource_path('images/fl-studio-open-button.png'), grayscale=True, confidence=0.8)
    pyautogui.click(openButton)

    pyautogui.write(path) # Enters the path of the file
    pyautogui.press('enter') # Presses Enter to open the file

    # Wait for the file to load
    time.sleep(10)

    # Check if the file has any problems, if so, ignore them
    if fl_project_contains_problems():
        printProgressBar(projects_saved, project_count, prefix = 'Progress:', suffix = path + " ⚠ Problems found - ignoring...", length = 50)
        okToProblems = pyautogui.locateCenterOnScreen(resource_path('images/fl-studio-loading-problems-ok.png'), grayscale=True, confidence=0.8)
        pyautogui.click(okToProblems)

    fileTabLocation = pyautogui.locateOnScreen(resource_path('images/fl-studio-file-tab.png'), grayscale=True, confidence=0.8)
    pyautogui.click(fileTabLocation)

    exportButton =  pyautogui.locateOnScreen(resource_path('images/fl-studio-export-button.png'), grayscale=True, confidence=0.8)
    pyautogui.click(exportButton)

    time.sleep(1)

    exportButton =  pyautogui.locateOnScreen(resource_path('images/fl-studio-export-zipped.png'), grayscale=True, confidence=0.8)
    pyautogui.click(exportButton)

    pyautogui.write(path.removesuffix("flp") + "zip") # Enters the path of the file
    pyautogui.press('enter') # Presses Enter to save the file

    # Check for overwrite error
    if has_overwrite_problem():
        if allowOverwrite:
            pyautogui.press('left')
            pyautogui.press("enter")
        else:
            pyautogui.press('enter')
            pyautogui.press('esc')

    # Wait for the file to load
    while fl_processing_zip():
        time.sleep(1)

    projects_saved += 1

def recursive_delete(directory):
    for file in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, file)):
            recursive_delete(os.path.join(directory, file))
        else:
            filename = os.fsdecode(file)
            #if filename.endswith(".flp"):
            #    save_project(os.path.join(directory, filename))

try:
    recursive_save(os.fsdecode(folderName))

    if deleteAudiosAfterExporting:
        print("\nDeleting audio files...")
        recursive_delete(os.fsdecode(folderName))

    print("\nAll done!")
except pyautogui.ImageNotFoundException:
    sys.exit("\nFL Studio not found. Make sure FL Studio is open and its gui scale is set to 100%.")