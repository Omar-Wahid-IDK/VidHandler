import os
import shutil
import re

# --------------------------------------------------------------------------------- Folders
VID_FOLDER = r"C:\Users\Omar\Downloads\Video"
Youtube_folder = r"E:\Media Player\Videos\Youtube"
Anime_folder = r"E:\Media Player\Videos\Anime"
SORTED_FOLDERS = {}

# Populate SORTED_FOLDERS with YouTube folders
for Folder in os.listdir(Youtube_folder):
    Folder_Path = os.path.join(Youtube_folder, Folder)
    if not os.path.isdir(Folder_Path):
        continue
    SORTED_FOLDERS[Folder.lower()] = Folder_Path

# Populate SORTED_FOLDERS with Anime folders
for Folder in os.listdir(Anime_folder):
    Folder_Path = os.path.join(Anime_folder, Folder)
    if not os.path.isdir(Folder_Path):
        continue
    SORTED_FOLDERS[Folder.lower()] = Folder_Path

print(SORTED_FOLDERS)
# -------------------------------------------------------------------------------- Check if this vid is anime or not
def is_anime_video(filename):
    """Heuristically checks if a filename looks like an anime episode."""
    return bool(re.search(r'-\s?\d{1,3}.*\d{3,4}p', filename.lower()))

# --------------------------------------------------------------------------------- Ensure Folders Exist
for key, folder in SORTED_FOLDERS.items():
    folder = folder.strip()
    SORTED_FOLDERS[key] = folder
    print(f"Checking folder: {repr(folder)}")
    if not os.path.exists(folder):
        print(f"Creating folder: {folder}")
        os.makedirs(folder, exist_ok=True)

# --------------------------------------------------------------------------------- Anime Season Detection
def get_anime_folder_and_season(filename):
    """Returns the correct folder and season subfolder if it's an anime episode."""
    if not is_anime_video(filename):
        return None 
# Clean up filename to extract the anime name
    name_without_ext = os.path.splitext(filename)[0]

# Remove resolution, episode numbers, and season tags
    cleaned_name = re.sub(r's\d+', '', name_without_ext, flags=re.IGNORECASE)         # Remove S1, S2
    cleaned_name = re.sub(r'-?\s*\d{1,3}.*\d{3,4}p.*$', '', cleaned_name, flags=re.IGNORECASE)  # Remove "-01 1080P"
    cleaned_name = re.sub(r'[^\w\s\-]', '', cleaned_name)                             # Remove special characters

# Normalize spacing
    cleaned_name = cleaned_name.strip()
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

# Remove common leading filler words (case-insensitive, whole word match)
    cleaned_name = re.sub(r'(?i)^(ah|a|an|the)\b\s*', '', cleaned_name)

    if not cleaned_name:
        cleaned_name = "Etc"


    anime_key = cleaned_name.lower()
    base_folder = os.path.join(Anime_folder, cleaned_name.title())

    # Add base folder if new
    if anime_key not in SORTED_FOLDERS:
        SORTED_FOLDERS[anime_key] = base_folder

    # Detect season number
    season_match = re.search(r's(\d+)', filename.lower())
    if season_match:
        season_num = season_match.group(1)
        season_folder_name = f"Season ({season_num})"
        full_season_path = os.path.join(base_folder, season_folder_name)
    else:
        # Default to Season (1) if not specified and if subfolders exist
        season_folders = [f for f in os.listdir(base_folder) if re.match(r'Season \(\d+\)', f)] if os.path.exists(base_folder) else []
        if season_folders:
            full_season_path = os.path.join(base_folder, "Season (1)")
        else:
            full_season_path = base_folder

    if not os.path.exists(full_season_path):
        os.makedirs(full_season_path, exist_ok=True)

    return full_season_path

# --------------------------------------------------------------------------------- General Folder Detection
def get_channel_folder(filename):
    """Returns the correct folder based on the channel name before the '-' or 'Etc' if invalid."""
    name_without_ext = os.path.splitext(filename)[0]

    # Match format like "ChannelName - VideoTitle"
    match = re.match(r'^(.+?)\s*-\s+.+', name_without_ext)
    if match:
        channel_name = match.group(1).strip()

        # Accept if 1–4 words, only basic punctuation (alphanum, space, dash, dot, apostrophe, underscore)
        if len(channel_name.split()) > 4 or not re.match(r'^[\w\s\-\.\']+$', channel_name):
            channel_name = "Etc"
    else:
        channel_name = "Etc"

    # Clean up the channel name
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s\-\.\']', '', channel_name)
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()

    if not cleaned_name:
        cleaned_name = "Etc"

    # 🔹 Folder path
    new_folder_path = os.path.join(Youtube_folder, cleaned_name)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path, exist_ok=True)

    # 🔹 Add to SORTED_FOLDERS for reuse
    SORTED_FOLDERS[cleaned_name.lower()] = new_folder_path

    return new_folder_path

# --------------------------------------------------------------------------------- Video Moving
def move_videos():
    """Move videos to their respective folders based on channel names and seasons."""
    moved_files = 0

    for file in os.listdir(VID_FOLDER):
        src = os.path.join(VID_FOLDER, file)

        if not os.path.isfile(src):
            continue

        anime_dest = get_anime_folder_and_season(file)
        dest_folder = anime_dest if anime_dest else get_channel_folder(file)

        if dest_folder.startswith(VID_FOLDER):
            print(f"⚠️ Skipping {file}: Preventing accidental nesting.")
            continue

        dest = os.path.join(dest_folder, file)

        try:
            shutil.move(src, dest)
            print(f"✅ Moved: {file} → {dest_folder}")
            moved_files += 1
        except Exception as e:
            print(f"❌ Error moving {file}: {e}")

    if moved_files == 0:
        print("No videos found to move.")

# --------------------------------------------------------------------------------- Run the script
if __name__ == "__main__":
    print(f"Sorting videos from: {VID_FOLDER}")
    move_videos()
