import os
import re

# Paths
VID_FOLDER = r"C:\Users\Omar\Downloads\Video"
CHANNELS_FILE = r"E:\Projects\VidHandler\VidHandler\Txt Files\youtube_channels.txt"
ANIME_FILE = r"E:\Projects\VidHandler\VidHandler\Txt Files\anime_name.txt"

# 🔹 Load YouTube channel names from the file
def get_channel_mapping():
    channel_mapping = {}
    
    try:
        with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) == 2:
                    video_title, channel_name = parts
                    channel_mapping[clean_text(video_title)] = channel_name  # Store cleaned title for matching
                else:
                    print(f"⚠ Skipping invalid line: {line.strip()} (wrong format)")
    except FileNotFoundError:
        print(f"❌ ERROR: File {CHANNELS_FILE} not found!")
    
    print(f"✅ Loaded {len(channel_mapping)} entries from {CHANNELS_FILE}")
    return channel_mapping

# 🔹 Load Anime names from the file
def get_anime_mapping():
    anime_mapping = {}
    try:
        with open(ANIME_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) == 2:
                    jp, en = parts
                    pattern = re.compile(re.escape(clean_text(jp)), re.IGNORECASE)
                    anime_mapping[pattern] = en
    except FileNotFoundError:
        print(f"❌ ERROR: File {ANIME_FILE} not found!")
    print(f"🎌 Loaded {len(anime_mapping)} anime entries from {ANIME_FILE}")
    return anime_mapping

# 🔹 Function to clean text (remove special characters, numbers, etc.)
def clean_text(text):
    """Convert filename to a standard format for matching."""
    text = text.lower()
    text = text.replace("_", " ").replace("/", " ")  # Treat both underscores and slashes as spaces
    text = text.replace(":", " ")  # Treat colons as spaces
    text = re.sub(r"[^\w\s]", "", text)  # Remove other special characters
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    return text

# 🔹 Sanitize filenames for Windows compatibility
def sanitize_filename(name):
    """Replace illegal characters in Windows filenames."""
    name = name.replace(":", " ")  # Replace colon with space
    return re.sub(r'[<>"/\\|?*]', '', name)  # Remove other forbidden characters

# 🔹 Rename video files with the correct channel name
def rename_videos():
    # Load mappings
    channel_mapping = get_channel_mapping()
    anime_mapping = get_anime_mapping()
    
    print(f"🔍 Scanning folder: {VID_FOLDER}")
    
    # 🔄 Rename normal videos first
    print("🔄 Renaming normal videos...")
    for file in os.listdir(VID_FOLDER):
        file_path = os.path.join(VID_FOLDER, file)
        if not os.path.isfile(file_path):
            continue  # Skip if it's not a file
        
        # 🔹 Clean filename before matching
        file_name, file_ext = os.path.splitext(file)
        clean_name = clean_text(file_name)

        # 🔹 Try to find a match in youtube_channels.txt
        matched_channel = None
        for video_title, channel_name in channel_mapping.items():
            if video_title in clean_name:  # Check if cleaned title is in filename
                matched_channel = channel_name
                break  # Stop searching once we find a match
        
        # Rename normal videos with channel name
        if matched_channel:
            new_file_name = f"{matched_channel} - {file}"
            new_file_name = sanitize_filename(new_file_name)  # Sanitize filename
            new_file_path = os.path.join(VID_FOLDER, new_file_name)
            os.rename(file_path, new_file_path)
            print(f"✅ Renamed: {file} → {new_file_name}")
        else:
            print(f"⚠ No match found for: {file}")
    
    # 🔄 Rename anime videos
    print("🔄 Renaming anime videos...")
    for file in os.listdir(VID_FOLDER):
        file_path = os.path.join(VID_FOLDER, file)
        if not os.path.isfile(file_path):
            continue  # Skip if it's not a file

        # 🔹 Check for anime match
        anime_found = False
        for pattern, en_name in anime_mapping.items():
            if pattern.search(clean_text(file)):
                new_base_name = pattern.sub(en_name, file)
                new_base_name = sanitize_filename(new_base_name)  # Sanitize filename
                new_file_path = os.path.join(VID_FOLDER, new_base_name)
                os.rename(file_path, new_file_path)
                print(f"🎌 Anime renamed: {file} → {new_base_name}")
                anime_found = True
                break
        
        if not anime_found:
            print(f"⚠ No anime match found for: {file}")
    
    # Clean up youtube_channels.txt (optional)
    open(CHANNELS_FILE, "w").close()
    print("🧹 youtube_channels.txt cleared!")

# Run the script
if __name__ == "__main__":
    rename_videos()
