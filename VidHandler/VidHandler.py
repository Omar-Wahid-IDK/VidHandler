import subprocess
import time

# Scripts
CodeCaller = r"E:\Projects\VidHandler\VidHandler\Scripts\CodeCaller.py"

def runpyfile():
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW

    subprocess.Popen(["python", CodeCaller], creationflags=CREATE_NO_WINDOW)

if __name__ == "__main__":
    runpyfile()
    