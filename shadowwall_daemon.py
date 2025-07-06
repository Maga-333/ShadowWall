from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from realtime_monitor import analyze_link  # <-- Make sure analyze_link uses VirusTotal + danger list
import pyperclip, time, json
from colorama import Fore, init
import os
from urllib.parse import urlparse

init(autoreset=True)

scanned_reports = []
driver = None

# 📂 Check Domain in Safe/Danger Lists
def check_domain_status(domain):
    domain = domain.lower()
    try:
        with open("data/danger_domains.txt", "r") as f:
            if domain in [line.strip().lower() for line in f]:
                return "danger"
    except: pass
    
    try:
        with open("data/safe_domains.txt", "r") as f:
            if domain in [line.strip().lower() for line in f]:
                return "safe"
    except: pass

    return "unknown"

# 🧒 Update HTML Report Page
def update_html_dashboard():
    with open("shadowwall_alert.html", "w") as f:
        f.write("""
        <html>
        <head>
            <title>🚨 ShadowWall Dashboard</title>
            <script>
              window.onload = function() {
                document.querySelectorAll("input[type='password']").forEach(el => el.disabled = true);
                document.querySelectorAll("form").forEach(form => {
                  form.addEventListener("submit", function(e) {
                    e.preventDefault();
                    alert("🛘 ShadowWall blocked password submission on this fake site!");
                  });
                });
              };
            </script>
        </head>
        <body style=\"background:black; color:white; font-family:sans-serif; padding:20px;\">
            <h1 style=\"color:yellow; text-align:center;\">🛡️ ShadowWall Live Report</h1>
        """)

        for report in scanned_reports:
            result = json.dumps({k: v for k, v in report['data'].items() if k != "VirusTotal"}, indent=2)
            border_color = "red" if report["data"].get("Fake") else "green"
            title_color = "red" if report["data"].get("Fake") else "lime"
            f.write(f"""
                <div style='border:2px solid {border_color}; padding:15px; margin-bottom:20px; border-radius:10px;'>
                    <h2 style='color:{title_color};'>🔗 {report["url"]}</h2>
                    <pre style='background:#222; color:orange; padding:10px; border-radius:8px;'>{result}</pre>
                </div>
            """)

        f.write("</body></html>")

# 🌐 Launch Browser Without Loading Any Site
def launch_browser_blank():
    global driver
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

# 🦪 Refresh Dashboard
def open_dashboard():
    dashboard_path = "file://" + os.path.abspath("shadowwall_alert.html")
    driver.get(dashboard_path)

# 🔀 Detect All Sources
def monitor_all_sources():
    print(Fore.CYAN + "\n🛡️ ShadowWall Real-Time Monitor Started...\n")
    clipboard_history = set()
    browser_history = set()
    last_clip = ""

    try:
        while True:
            try:
                current_clip = pyperclip.paste().strip()
                if current_clip.startswith("http") and current_clip != last_clip:
                    print(Fore.YELLOW + f"\n🗌 Copied Link: {current_clip}")
                    result = analyze_link(current_clip)

                    # 🌐 Domain check logic
                    domain = urlparse(current_clip).netloc.lower()
                    status = check_domain_status(domain)
                    if status == "danger":
                        result["Fake"] = True
                    elif status == "safe":
                        result["Fake"] = False

                    show_report(result, current_clip)
                    last_clip = current_clip
                    clipboard_history.add(current_clip)
            except Exception as e:
                print(Fore.RED + f"Clipboard error: {e}")

            try:
                if driver:
                    browser_url = driver.current_url.strip()
                    if (
                        browser_url.startswith("http")
                        and "example.com" not in browser_url
                        and browser_url not in browser_history
                    ):
                        print(Fore.YELLOW + f"\n🌐 Browser URL Visited: {browser_url}")
                        result = analyze_link(browser_url)

                        # 🌐 Domain check logic
                        domain = urlparse(browser_url).netloc.lower()
                        status = check_domain_status(domain)
                        if status == "danger":
                            result["Fake"] = True
                        elif status == "safe":
                            result["Fake"] = False

                        show_report(result, browser_url)
                        browser_history.add(browser_url)
            except Exception as e:
                print(Fore.RED + f"Browser read error: {e}")

            time.sleep(2)

    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n⛔ ShadowWall Monitoring Stopped.")
        if driver:
            driver.quit()

# 🤔 Report Display
def show_report(result, url):
    scanned_reports.append({"url": url, "data": result})
    update_html_dashboard()
    open_dashboard()

    if result.get("Fake"):
        print(Fore.RED + "🚨 FAKE/SUSPICIOUS SITE DETECTED!")
    else:
        print(Fore.GREEN + "✅ SAFE SITE")

    # Print final output except VirusTotal
    filtered_result = {k: v for k, v in result.items() if k != "VirusTotal"}
    print(Fore.GREEN + json.dumps(filtered_result, indent=2))

# 🚀 Entry Point
def main():
    launch_browser_blank()
    monitor_all_sources()

if __name__ == "__main__":
    main()
