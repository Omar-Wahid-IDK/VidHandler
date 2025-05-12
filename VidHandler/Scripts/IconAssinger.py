import os
import subprocess

def normalize_name(name):
    # Normalize by converting to lowercase and removing spaces or underscores
    return name.lower().replace(" ", "").replace("_", "")

def set_folder_icon(folder_path, icon_path):
    desktop_ini_path = os.path.join(folder_path, 'desktop.ini')

    # Write desktop.ini with full icon path
    with open(desktop_ini_path, 'w') as f:
        f.write(f"""[.ShellClassInfo]
IconResource={icon_path},0
ConfirmFileOp=0
""")

    # Set file attributes: Hidden only (not System)
    subprocess.run(['attrib', '+h', desktop_ini_path], shell=True)
    subprocess.run(['attrib', '+r', folder_path], shell=True)

def apply_icon_to_folder(folder_path, icon_filename, icons_folder):
    icon_path = os.path.join(icons_folder, icon_filename)
    desktop_ini_path = os.path.join(folder_path, 'desktop.ini')

    if os.path.isdir(folder_path):
        # Skip if desktop.ini already exists
        if os.path.exists(desktop_ini_path):
            print(f"Icon already set for: {folder_path}")
            return

        try:
            set_folder_icon(folder_path, icon_path)
            print(f"Applied {icon_filename} to {folder_path}")
        except PermissionError as e:
            print(f"Permission denied for {folder_path}: {e}")
    else:
        print(f"Folder not found: {folder_path}")

# Main
icons_folder = 'E:/Icons/Ico'
base_folder = 'E:/Media Player/Videos/Youtube'

# Get icon files and folders
icon_files = os.listdir(icons_folder)
folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

for folder in folders:
    normalized_folder = normalize_name(folder)
    matched_icon = None

    for icon in icon_files:
        if normalized_folder in normalize_name(icon):
            matched_icon = icon
            break

    if matched_icon:
        folder_path = os.path.join(base_folder, folder)
        apply_icon_to_folder(folder_path, matched_icon, icons_folder)
    else:
        print(f"No matching icon found for {folder}")
    print("-" * 30)
