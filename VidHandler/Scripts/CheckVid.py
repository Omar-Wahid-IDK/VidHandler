import os
import shutil

# Define the parent folder
parent_folder = r"E:\Media Player\Videos\Youtube"

# Define common video file extensions
video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"}

# Iterate through subfolders in the parent directory
for folder in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder)

    # Check if it's a folder
    if os.path.isdir(folder_path):
        # Check for video files inside the folder
        contains_videos = any(
            file.lower().endswith(tuple(video_extensions))
            for file in os.listdir(folder_path)
        )

        # Append check mark if videos are found and it's not already marked
        if contains_videos and "✔" not in folder:
            new_folder_name = f"{folder} ✔"
            new_folder_path = os.path.join(parent_folder, new_folder_name)
            shutil.move(folder_path, new_folder_path)
            print(f"Marked: {new_folder_name}")

        # Remove check mark if no videos are found
        elif not contains_videos and "✔" in folder:
            new_folder_name = folder.replace(" ✔", "")
            new_folder_path = os.path.join(parent_folder, new_folder_name)
            shutil.move(folder_path, new_folder_path)
            print(f"Unmarked: {new_folder_name}")