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
        full_path = os.path.join(directory, file)
        if os.path.isdir(full_path):
            count += count_files_recursively(full_path)  # <-- fixed here
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

def fl_loading_project(retry):
    # Check for loading label
    try:
        pyautogui.locateOnScreen(resource_path('images/fl-studio-loading.png'), grayscale=True, confidence=0.8)
        return True
    except:
        if retry == 0:
            return False
        else:
            time.sleep(1)
            return fl_loading_project(retry-1)

def locate_on_screen(image_name):
    image_path = resource_path(f'images/{image_name}')
    try:
        return pyautogui.locateOnScreen(image_path, grayscale=True, confidence=0.7)
    except pyautogui.ImageNotFoundException:
        raise pyautogui.ImageNotFoundException(f"Image not found: {image_path}")

def cursor_is_loading():
    print(win32gui.GetCursorInfo())

projects_saved = 0

def save_project(path):
    global projects_saved
    printProgressBar(projects_saved, project_count, prefix = 'Progress:', suffix = path, length = 50)

    fileTabLocation = locate_on_screen('fl-studio-file-tab.png')
    pyautogui.click(fileTabLocation)

    openButton = locate_on_screen('fl-studio-open-button.png')
    pyautogui.click(openButton)

    time.sleep(1)

    pyautogui.write(path) # Enters the path of the file
    pyautogui.press('enter') # Presses Enter to open the file

    # Wait for the project to load
    while fl_loading_project(3):
        time.sleep(1)

    # Check if the file has any problems, if so, ignore them
    if fl_project_contains_problems():
        printProgressBar(projects_saved, project_count, prefix = 'Progress:', suffix = path + " ⚠ Problems found - ignoring...", length = 50)
        okToProblems = pyautogui.locateCenterOnScreen(resource_path('images/fl-studio-loading-problems-ok.png'), grayscale=True, confidence=0.8)
        pyautogui.click(okToProblems)

    fileTabLocation = locate_on_screen('fl-studio-file-tab.png')
    pyautogui.click(fileTabLocation)

    time.sleep(.5)

    exportButton =  locate_on_screen('fl-studio-export-button.png')
    pyautogui.click(exportButton)

    time.sleep(1)

    exportButton = locate_on_screen('fl-studio-export-zipped.png')
    pyautogui.click(exportButton)

    pyautogui.write(path.removesuffix("flp") + "zip") # Enters the path of the file
    pyautogui.press('enter') # Presses Enter to save the file

    time.sleep(1) # Wait for windows file explorer to open

    # Check for overwrite error
    if has_overwrite_problem():
        if allowOverwrite:
            pyautogui.press('left')
            pyautogui.press("enter")
        else:
            pyautogui.press('enter')
            pyautogui.press('esc')

    time.sleep(1) # Wait for windows file explorer to

    # Wait for the project to be exported
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
except pyautogui.ImageNotFoundException as e:
    sys.exit(f"\nError: {e}\nMake sure FL Studio is open and its GUI scale is set to 100%.")