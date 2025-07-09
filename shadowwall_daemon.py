from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from realtime_monitor import analyze_link
import pyperclip, time, json
from colorama import Fore, init
import os
from urllib.parse import urlparse

init(autoreset=True)

scanned_reports = []
driver = None
tab_opened = False  # ✅ Track if tab already opened


# ✅ Auto-create safe/danger files if missing
def ensure_domain_files():
    os.makedirs("data", exist_ok=True)
    for fname in ["safe_domains.txt", "danger_domains.txt"]:
        path = os.path.join("data", fname)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("")  # empty file


# 🔍 Check if domain is safe or dangerous
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


# 🧠 Create/update HTML dashboard
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
                window.scrollTo(0, document.body.scrollHeight);
              };
            </script>
        </head>
        <body style="background:black; color:white; font-family:sans-serif; padding:20px;">
            <h1 style="color:yellow; text-align:center;">🛡️ ShadowWall Live Report</h1>
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


# 🌐 Launch Chrome (only when needed)
def launch_browser_blank():
    global driver
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)


# 🔁 Open or refresh same tab only when needed
def open_dashboard():
    global tab_opened
    dashboard_path = "file://" + os.path.abspath("shadowwall_alert.html")

    try:
        if not tab_opened:
            driver.get(dashboard_path)
            tab_opened = True
        elif driver.current_url.startswith("file://") and "shadowwall_alert.html" in driver.current_url:
            driver.execute_script("location.reload(true);")
        else:
            driver.get(dashboard_path)
    except:
        driver.get(dashboard_path)
        tab_opened = True


# 🕵️ Real-time monitor (clipboard + browser)
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

                    domain = urlparse(current_clip).netloc.lower()
                    status = check_domain_status(domain)
                    if status == "danger":
                        result["Fake"] = True
                    elif status == "safe":
                        result["Fake"] = False

                    if result:
                        if not driver:
                            launch_browser_blank()
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

                        domain = urlparse(browser_url).netloc.lower()
                        status = check_domain_status(domain)
                        if status == "danger":
                            result["Fake"] = True
                        elif status == "safe":
                            result["Fake"] = False

                        if result:
                            show_report(result, browser_url)
                            browser_history.add(browser_url)
            except Exception as e:
                print(Fore.RED + f"Browser read error: {e}")

            time.sleep(2)

    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n⛔ ShadowWall Monitoring Stopped.")
        if driver:
            driver.quit()


# 📢 Show live report
def show_report(result, url):
    scanned_reports.append({"url": url, "data": result})
    update_html_dashboard()
    open_dashboard()

    if result.get("Fake"):
        print(Fore.RED + "🚨 FAKE/SUSPICIOUS SITE DETECTED!")
    else:
        print(Fore.GREEN + "✅ SAFE SITE")

    filtered = {k: v for k, v in result.items() if k != "VirusTotal"}
    print(Fore.GREEN + json.dumps(filtered, indent=2))


# 🚀 Entry
def main():
    ensure_domain_files()
    monitor_all_sources()  # browser only launches on demand

if __name__ == "__main__":
    main()
