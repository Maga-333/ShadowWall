# 🔐 ShadowWall Daemon - Final Stable Version (Fix: Repeated Clipboard, Exit Crash, Redirection Fail)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from colorama import Fore, init

import pyperclip
import time
import json
import os
import requests

init(autoreset=True)

scanned_reports = []
driver = None
tab_opened = False

# ⚠️ Known fake IPs
known_fake_ips = [
    "104.21.64.1",
    "185.199.108.153",
    "198.51.100.23",
    "203.0.113.1"
]

# ✅ Load keywords

def load_payload_keywords():
    try:
        with open("data/payload_keywords.txt", "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except:
        return []

payload_keywords = load_payload_keywords()


def ensure_domain_files():
    os.makedirs("data", exist_ok=True)
    for fname in ["safe_domains.txt", "danger_domains.txt", "payload_keywords.txt"]:
        path = os.path.join("data", fname)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("")


def check_domain_status(domain):
    domain = domain.lower()
    try:
        with open("data/danger_domains.txt", "r") as f:
            if domain in [line.strip().lower() for line in f]:
                return "danger"
    except:
        pass
    try:
        with open("data/safe_domains.txt", "r") as f:
            if domain in [line.strip().lower() for line in f]:
                return "safe"
    except:
        pass
    return "unknown"


def contains_danger_keywords(url):
    url_lower = url.lower()
    for kw in payload_keywords:
        if kw in url_lower:
            return kw
    return None


def get_ip_and_country(domain):
    try:
        ip = requests.get(f"https://dns.google/resolve?name={domain}").json()["Answer"][0]["data"]
        ip_data = requests.get(f"https://ipinfo.io/{ip}/json").json()
        return ip, ip_data.get("country", None)
    except:
        return None, None


def get_redirections(url):
    try:
        res = requests.get(url, timeout=10, allow_redirects=True)
        history = [(r.url, r.status_code) for r in res.history]
        history.append((res.url, res.status_code))
        return history, False
    except:
        return [(url, 0)], True


def launch_browser_blank():
    global driver
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)


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
                    alert("🚘 ShadowWall blocked password submission on this fake site!");
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
            result = json.dumps({k: v for k, v in report['data'].items()}, indent=2)
            border_color = "red" if report["data"].get("Fake") else "green"
            title_color = "red" if report["data"].get("Fake") else "lime"

            redir_html = "<ul style='color:white;'>"
            for item in report["data"].get("Redirections", []):
                redir_html += f"<li>{item[0]} - Status: {item[1]}</li>"
            redir_html += "</ul>"

            f.write(f"""
                <div style='border:2px solid {border_color}; padding:15px; margin-bottom:20px; border-radius:10px;'>
                    <h2 style='color:{title_color};'>🔗 {report["url"]}</h2>
                    <pre style='background:#222; color:orange; padding:10px; border-radius:8px;'>{result}</pre>
                    <h3 style='color:white;'>🔁 Redirection Path:</h3>
                    {redir_html}
                </div>
            """)
        f.write("</body></html>")


def show_report(result, url):
    scanned_reports.append({"url": url, "data": result})
    update_html_dashboard()
    open_dashboard()
    if result.get("Fake"):
        print(Fore.RED + "🚨 FAKE/SUSPICIOUS SITE DETECTED!")
    else:
        print(Fore.GREEN + "✅ SAFE SITE")
    print(Fore.CYAN + json.dumps(result, indent=2))


def monitor_all_sources():
    print(Fore.CYAN + "\n🛡️ ShadowWall Real-Time Monitor Started...\n")
    clipboard_history = set()
    browser_history = set()
    last_clip = pyperclip.paste().strip()

    try:
        while True:
            try:
                current_clip = pyperclip.paste().strip()
                if current_clip.startswith("http") and current_clip != last_clip and current_clip not in clipboard_history:
                    print(Fore.YELLOW + f"\n📋 Copied Link: {current_clip}")
                    domain = urlparse(current_clip).netloc.lower()
                    redirs, redir_error = get_redirections(current_clip)
                    ip, country = get_ip_and_country(domain)

                    reasons = []
                    status = check_domain_status(domain)
                    if status == "danger": reasons.append("Dangerous domain")
                    payload_kw = contains_danger_keywords(current_clip)
                    if payload_kw: reasons.append(f"Payload keyword: {payload_kw}")
                    if redir_error: reasons.append("Redirection failed")
                    if not ip: reasons.append("No IP found")
                    elif ip in known_fake_ips: reasons.append("IP flagged as suspicious")

                    result = {
                        "url": current_clip,
                        "Domain": domain,
                        "IP": ip,
                        "Redirections": redirs,
                        "Final URL": current_clip,
                        "Final Domain": domain,
                        "Final IP": ip,
                        "Final Country": country,
                        "Payload Keyword": payload_kw,
                        "IP Flagged": ip in known_fake_ips if ip else "No IP",
                        "Redirection Error": redir_error,
                        "Fake": len(reasons) > 0,
                        "Reasons": reasons
                    }

                    if not driver:
                        launch_browser_blank()
                    show_report(result, current_clip)
                    last_clip = current_clip
                    clipboard_history.add(current_clip)

                    if redir_error or ip is None:
                        time.sleep(5)
            except Exception as e:
                print(Fore.RED + f"Clipboard error: {e}")

            try:
                if driver:
                    browser_url = driver.current_url.strip()
                    if browser_url.startswith("http") and "example.com" not in browser_url and browser_url not in browser_history:
                        print(Fore.YELLOW + f"\n🌐 Browser URL Visited: {browser_url}")
                        domain = urlparse(browser_url).netloc.lower()
                        redirs, redir_error = get_redirections(browser_url)
                        ip, country = get_ip_and_country(domain)

                        reasons = []
                        status = check_domain_status(domain)
                        if status == "danger": reasons.append("Dangerous domain")
                        payload_kw = contains_danger_keywords(browser_url)
                        if payload_kw: reasons.append(f"Payload keyword: {payload_kw}")
                        if redir_error: reasons.append("Redirection failed")
                        if not ip: reasons.append("No IP found")
                        elif ip in known_fake_ips: reasons.append("IP flagged as suspicious")

                        result = {
                            "url": browser_url,
                            "Domain": domain,
                            "IP": ip,
                            "Redirections": redirs,
                            "Final URL": browser_url,
                            "Final Domain": domain,
                            "Final IP": ip,
                            "Final Country": country,
                            "Payload Keyword": payload_kw,
                            "IP Flagged": ip in known_fake_ips if ip else "No IP",
                            "Redirection Error": redir_error,
                            "Fake": len(reasons) > 0,
                            "Reasons": reasons
                        }

                        show_report(result, browser_url)
                        browser_history.add(browser_url)

                        if result["Fake"]:
                            driver.execute_script("""
                                alert("⛔ This site is suspicious. ShadowWall has blocked password fields.");
                                document.querySelectorAll("input[type='password']").forEach(el => el.disabled = true);
                                document.querySelectorAll("form").forEach(form => {
                                  form.addEventListener("submit", function(e) {
                                    e.preventDefault();
                                    alert("🚫 Password submission blocked by ShadowWall!");
                                  });
                                });
                            """)
            except Exception as e:
                print(Fore.RED + f"Browser error: {e}")

            time.sleep(2)
    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n❌ ShadowWall Monitoring Stopped by user.")
        if driver:
            driver.quit()


def main():
    ensure_domain_files()
    monitor_all_sources()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n❌ ShadowWall exited cleanly.")
        if driver:
            driver.quit()
