import pyperclip
import time
import os
import sys
import winsound
from plyer import notification

FILE_NAME = r"E:\Projects\VidHandler\VidHandler\Txt Files\youtube_links.txt"
INACTIVITY_TIMEOUT = 5  # seconds

# Ensure directory and file exist
os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
if not os.path.exists(FILE_NAME):
    open(FILE_NAME, "w").close()

print(f"[INFO] Saving to: {os.path.abspath(FILE_NAME)}")

def get_saved_links():
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())
   
#def send_notification(title, message):
    #print(f"[NOTIFY] {title}: {message}")  # 👈 Debug print

    #MAX_LENGTH = 240
    #short_message = message if len(message) <= MAX_LENGTH else message[:MAX_LENGTH] + "..."

    #notification.notify(
        #title=title,
        #message=short_message,
        #timeout=0.2,
        #app_name="LinkCopier"
   #)

def save_link(link):
    link = link.strip()
    if not link:
        return

    saved_links = get_saved_links()
    if link not in saved_links:
        with open(FILE_NAME, "a", encoding="utf-8") as f:
            f.write(link + "\n")
        print(f"[ADDED] {link}")
        
        # Play a quick 'ding' sound
        winsound.Beep(3000, 150)  # Frequency: 1000 Hz, Duration: 200 ms
    else:
        print(f"[SKIPPED] {link} (already exists)")

def is_youtube_link(text):
    return any(domain in text for domain in [
        "youtube.com/watch?v=",
        "youtu.be/",
        "youtube.com/shorts/",
        "youtube.com/playlist?"
    ])

def get_clipboard_content():
    try:
        return pyperclip.paste().strip()
    except pyperclip.PyperclipException as e:
        print(f"[ERROR] Clipboard error: {e}")
        sys.exit(1)

def monitor_clipboard():
    last_content = ""
    last_active = time.time()

    while True:
        content = get_clipboard_content()
        
        if content != last_content and is_youtube_link(content):
            save_link(content)
            last_content = content
            last_active = time.time()

        if time.time() - last_active > INACTIVITY_TIMEOUT:
            print("[INFO] No new links for 5 seconds. Exiting...")
            break
        
        time.sleep(1)

if __name__ == "__main__":
    print("[INFO] Monitoring clipboard for YouTube links...")
    try:
        monitor_clipboard()
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
