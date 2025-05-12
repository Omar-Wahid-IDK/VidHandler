import subprocess
import time

# Scripts
GetChannelName = r"E:\Projects\VidHandler\VidHandler\Scripts\GetChannelName.py"
VidRenamer = r"E:\Projects\VidHandler\VidHandler\Scripts\NewRenamer.py"
CheckVidOpp = r"E:\Projects\VidHandler\VidHandler\Scripts\CheckVidOpp.py"
sort_videos = r"E:\Projects\VidHandler\VidHandler\Scripts\NewSort.py"
CheckVid = r"E:\Projects\VidHandler\VidHandler\Scripts\CheckVid.py"
IconGetter = r"E:\Projects\VidHandler\VidHandler\Scripts\IconGetter.py"
IconAssinger = r"E:\Projects\VidHandler\VidHandler\Scripts\IconAssinger.py"
CricledImages = r"E:\Projects\VidHandler\VidHandler\Scripts\CircledImages.py"
IcoConverter = r"E:\Projects\VidHandler\VidHandler\Scripts\IcoConverter.py"


def runpyfile():
    scripts = [
        GetChannelName,
        VidRenamer,
        CheckVidOpp,
        sort_videos,
        IconGetter,
        CricledImages,
        IcoConverter,
        IconAssinger,
        CheckVid
    ]

    for script in scripts:
        subprocess.run(["python", script], creationflags=subprocess.CREATE_NO_WINDOW)

if __name__ == "__main__":
    runpyfile()
    