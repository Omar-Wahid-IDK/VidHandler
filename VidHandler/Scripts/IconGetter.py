import os
import re
import requests
from PIL import Image
from io import BytesIO
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup

FOLDER_PATH = r"E:\Media Player\Videos\Youtube"
SAVE_PATH = r"E:\Icons\Png"
CHANNEL_LINKS_FILE = r"E:\Projects\VidHandler\VidHandler\Txt Files\channel_links.txt"

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def clean_channel_name(name):
    return name.replace(" ", "").replace("'", "")

def load_channel_links():
    channel_map = {}
    if os.path.exists(CHANNEL_LINKS_FILE):
        with open(CHANNEL_LINKS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if '|' in line:
                    name, handle = map(str.strip, line.split('|', 1))
                    channel_map[name] = handle
    return channel_map

def get_channel_info(video_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': 1,
        'skip_download': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(video_url, download=False)

def fallback_logo_scrape(channel_url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(channel_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    og_image = soup.find("meta", property="og:image")
    if og_image:
        return og_image["content"]
    return None

def download_logo_as_png(img_url, name):
    try:
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        os.makedirs(SAVE_PATH, exist_ok=True)
        filename = sanitize_filename(name) + ".png"
        full_path = os.path.join(SAVE_PATH, filename)
        img.save(full_path)
        print(f"✅ Saved logo as: {full_path}")
    except Exception as e:
        print(f"❌ Failed to download or save image for {name}: {e}")

def process_folder(folder_name, channel_map):
    folder_path = os.path.join(FOLDER_PATH, folder_name)

    if os.path.exists(os.path.join(folder_path, 'desktop.ini')):
        print(f"🛑 Skipping {folder_name}: desktop.ini found")
        return

    if os.path.exists(os.path.join(SAVE_PATH, f"{folder_name}.png")):
        print(f"✅ Icon already exists for {folder_name}")
        return

    print(f"🔍 Fetching icon for: {folder_name}")

    # 🔁 Use mapped channel handle if available
    lookup_key = folder_name.strip()
    if lookup_key in channel_map:
        channel_handle = channel_map[lookup_key]
    else:
        channel_handle = clean_channel_name(folder_name)

    url = f"https://www.youtube.com/@{channel_handle}"

    try:
        info = get_channel_info(url)
        if not info or not info.get("uploader_url"):
            print(f"❌ Could not get uploader info for {folder_name}.")
            return

        logo_url = fallback_logo_scrape(info["uploader_url"])
        if not logo_url:
            print(f"❌ Could not extract logo from channel page for {folder_name}.")
            return

        download_logo_as_png(logo_url, folder_name)

    except Exception as e:
        print(f"❌ Error fetching info for {url}: {e}")
        print(f"❌ Could not get uploader info for {folder_name}.")

def main():
    print("📁 Scanning videos for new channel icons...")
    channel_map = load_channel_links()
    for folder in os.listdir(FOLDER_PATH):
        folder_path = os.path.join(FOLDER_PATH, folder)
        if os.path.isdir(folder_path):
            process_folder(folder, channel_map)

if __name__ == "__main__":
    main()
