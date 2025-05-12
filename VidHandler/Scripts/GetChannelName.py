import os
import re
import requests
import html
from concurrent.futures import ProcessPoolExecutor

# 📂 File Paths
VIDEO_LINKS_FILE = r"E:\Projects\VidHandler\VidHandler\Txt Files\youtube_links.txt"
CHANNELS_FILE = r"E:\Projects\VidHandler\VidHandler\Txt Files\youtube_channels.txt"
CHANNEL_LINKS_FILE = r"E:\Projects\VidHandler\VidHandler\Txt Files\channel_links.txt"

# 🔹 Function to get video title, channel name, and channel handle
def get_video_details(youtube_url):
    try:
        response = requests.get(youtube_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Error fetching: {youtube_url} (status {response.status_code})")
            return None, None, None, None

        html_text = response.text

        # ✅ Extract and decode video title
        title_match = re.search(r'<title>(.*?)</title>', html_text)
        title = html.unescape(title_match.group(1)).replace(" - YouTube", "").strip() if title_match else None

        # ✅ Extract channel name
        channel_match = re.search(r'ownerChannelName":"(.*?)"', html_text)
        channel_name = html.unescape(channel_match.group(1)).strip() if channel_match else None

        # ✅ Extract channel handle (e.g., "@SomeChannel")
        handle_match = re.search(r'"canonicalBaseUrl":"\/@(.*?)"', html_text)
        channel_handle = handle_match.group(1).strip() if handle_match else None

        return youtube_url, title, channel_name, channel_handle

    except Exception as e:
        print(f"❌ Exception on {youtube_url}: {e}")
        return None, None, None, None

# 🔹 Function to process all video links
def process_video_links():
    if not os.path.exists(VIDEO_LINKS_FILE):
        print(f"❌ ERROR: {VIDEO_LINKS_FILE} not found!")
        return

    with open(VIDEO_LINKS_FILE, "r", encoding="utf-8") as f:
        video_links = [line.strip() for line in f if line.strip()]

    if not video_links:
        print("⚠ No video links found.")
        return

    # Load existing entries to avoid duplicates
    existing_channels = set()
    existing_handles = set()

    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
            existing_channels = set(line.strip() for line in f if line.strip())

    if os.path.exists(CHANNEL_LINKS_FILE):
        with open(CHANNEL_LINKS_FILE, "r", encoding="utf-8") as f:
            existing_handles = set(line.strip() for line in f if line.strip())

    with open(CHANNELS_FILE, "a", encoding="utf-8") as f_channels, \
         open(CHANNEL_LINKS_FILE, "a", encoding="utf-8") as f_handles:

        with ProcessPoolExecutor() as executor:
            results = executor.map(get_video_details, video_links)

            for link, (url, title, channel_name, channel_handle) in zip(video_links, results):
                if title and channel_name:
                    # 🛠 Replace first '|' in title with '-' to avoid confusion
                    if "|" in title:
                        title = title.replace("|", "-", 1).strip()

                    channel_entry = f"{title} | {channel_name}"
                    if channel_entry not in existing_channels:
                        f_channels.write(channel_entry + "\n")
                        print(f"✅ Saved: {channel_entry}")
                        existing_channels.add(channel_entry)
                    else:
                        print(f"⏭ Skipped duplicate: {channel_entry}")

                    if channel_handle and channel_handle.lower() != channel_name.lower().replace(" ", ""):
                        handle_entry = f"{channel_name} | {channel_handle}"
                        if handle_entry not in existing_handles:
                            f_handles.write(handle_entry + "\n")
                            print(f"🔁 Mismatch saved: {handle_entry}")
                            existing_handles.add(handle_entry)
                        else:
                            print(f"⏭ Skipped duplicate handle: {handle_entry}")
                else:
                    print(f"⚠ Skipping: {link}")

    # Clean up the input file
    open(VIDEO_LINKS_FILE, "w").close()
    print("🧹 Cleaned up youtube_links.txt!")

# 🔹 Entry point
if __name__ == "__main__":
    process_video_links()
