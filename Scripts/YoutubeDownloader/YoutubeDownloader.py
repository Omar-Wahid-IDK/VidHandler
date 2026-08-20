import subprocess
import os
from pathlib import Path
import sys

base_dir = Path(__file__).resolve().parent.parent.parent
txt_dir = base_dir / "Txt Files"
download_folder = str(Path.home() / "Downloads" / "Video")
txt_file = txt_dir / "youtube_links.txt"
yt_dlp_executable = str(base_dir / "Runtime" / "Scripts" / "yt-dlp.exe")
node_executable = str(base_dir / "NodeRuntime" / "node.exe")
video_index = 0

# Verify tools exist upfront
if not Path(yt_dlp_executable).exists():
    print(f"CRITICAL: yt-dlp not found at {yt_dlp_executable}")
    sys.exit(1)
if not Path(node_executable).exists():
    print(f"CRITICAL: node not found at {node_executable}")
    sys.exit(1)

# Read requested quality from GUI argument (default to 360p if run standalone)
selected_quality = sys.argv[1] if len(sys.argv) > 1 else "360p"
height_val = selected_quality.replace("p", "")

#print("Python being used:", sys.executable)


# Smart Fallback Format String:
# 1. Try exact height
# 2. Try lower heights (fallback if exact doesn't exist)
# 3. Try higher heights 
# 4. Fallback to best overall stream
format_string = (
    f"bv*[height={height_val}]+ba/"
    f"bv*[height<={height_val}]+ba/"
    f"bv*[height>={height_val}]+ba/"
    f"b"
)

if not txt_file.exists():
    print(f"Error: {txt_file} not found.")
    sys.exit(1)

with open(txt_file, "r", encoding="utf-8") as file:
    urls = [line.strip() for line in file if line.strip()]

if len(urls) > 1:
    print(f"{len(urls)} Videos Found | Download Quality: {selected_quality}")
    print("-"*60)
elif len(urls) == 1:
    print(f"{len(urls)} Video Found | Download Quality: {selected_quality}")
    print("-"*60)
else:
    print("No Videos Found")

for url in urls:
    print(f"Downloading: {url}")
    video_index += 1
    
    subprocess.run([
        yt_dlp_executable,
        "--js-runtimes",
        f"node:{node_executable}",
        "--remote-components",
        "ejs:github",
        "-f",
        format_string,  # <--- Dynamic fallback format string
        "--merge-output-format",
        "mp4",
        "-P",
        download_folder,
        "-o",
        "%(title)s.%(ext)s",
        url,
        "--no-playlist"
    ])

    if video_index > 0:
        print(f"{"-"*82}[{video_index}/{len(urls)}]{"-"*82}")
