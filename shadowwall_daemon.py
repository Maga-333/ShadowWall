from realtime_monitor import analyze_link
import time, pyperclip

scanned_links = set()

def monitor_clipboard():
    while True:
        url = pyperclip.paste()
        if url.startswith("http") and url not in scanned_links:
            result = analyze_link(url)
            print("[ShadowWall Scan]")
            print(result)
            scanned_links.add(url)
        time.sleep(3)

monitor_clipboard()
