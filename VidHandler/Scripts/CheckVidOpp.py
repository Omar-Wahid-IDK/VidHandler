import os
import shutil

# Define the parent folder
parent_folder = r"E:\Media Player\Videos\Youtube"

# Iterate through subfolders in the parent directory
for folder in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder)

    # Check if it's a folder and contains a check mark
    if os.path.isdir(folder_path) and "✔" in folder:
        new_folder_name = folder.replace(" ✔", "")
        new_folder_path = os.path.join(parent_folder, new_folder_name)

        # Ensure there's no name conflict before renaming
        if not os.path.exists(new_folder_path):
            shutil.move(folder_path, new_folder_path)
            print(f"Check mark removed: {new_folder_name}")