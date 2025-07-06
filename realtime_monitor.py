import requests, socket
from urllib.parse import urlparse
from ipwhois import IPWhois

# ✅ Load Safe & Danger Domains + Payloads
def load_domain_lists():
    try:
        with open("data/safe_domains.txt") as f:
            safe_domains = set([d.strip().lower() for d in f if d.strip()])
    except:
        safe_domains = set()

    try:
        with open("data/danger_domains.txt") as f:
            danger_domains = set([d.strip().lower() for d in f if d.strip()])
    except:
        danger_domains = set()

    try:
        with open("data/payload_keywords.txt") as f:
            payload_keywords = [k.strip().lower() for k in f if k.strip()]
    except:
        payload_keywords = []

    return safe_domains, danger_domains, payload_keywords

# ✅ Extract domain & IP
def get_ip_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        ip = socket.gethostbyname(domain)
        return domain, ip
    except:
        return "Unknown", "Unknown"

# ✅ Redirection + WHOIS (Optional - not for blocking)
def check_redirection(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)

        redir_chain = [(resp.url, resp.status_code) for resp in r.history]
        redir_chain.append((r.url, r.status_code))

        final_domain = urlparse(r.url).netloc
        final_ip = socket.gethostbyname(final_domain)

        try:
            ip_data = IPWhois(final_ip).lookup_rdap()
            country = ip_data.get("network", {}).get("country", "Unknown")
            org = ip_data.get("network", {}).get("name", "Unknown")
        except:
            country = "Unknown"
            org = "Unknown"

        return redir_chain, r.url, final_domain, final_ip, country, org

    except Exception:
        return [("[Error] Redirection Failed", "N/A")], "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

# ✅ Check for payload keyword
def has_payload_keyword(url, payload_keywords):
    for keyword in payload_keywords:
        if keyword in url.lower():
            return keyword
    return None

# 🚧 Placeholder for VirusTotal (Simulated Clean)
def virustotal_check(url):
    # Replace with VT API call if needed
    return False

# 🔍 Main Analyzer
def analyze_link(url):
    safe_list, danger_list, payload_keywords = load_domain_lists()

    domain, ip = get_ip_domain(url)
    redirs, final_url, final_domain, final_ip, country, org = check_redirection(url)
    keyword = has_payload_keyword(url, payload_keywords)
    virus_check = virustotal_check(url)

    domain = domain.lower() if domain else "unknown"
    final_domain = final_domain.lower() if final_domain else "unknown"

    # ✅ Domain Presence Checks
    in_danger = domain in danger_list or final_domain in danger_list
    in_safe = domain in safe_list or final_domain in safe_list

    # ✅ Behavior-Based Suspicion
    suspicious_keyword = keyword is not None
    multiple_redirections = len(redirs) > 1

    # 🔐 Final Decision Logic
    is_fake = (
        in_danger or
        virus_check or
        suspicious_keyword or
        multiple_redirections
    )

    # 🟢 Force SAFE if explicitly listed
    if in_safe:
        is_fake = False

    # 🧾 Report Output
    print(f"\n🌐 Scanning URL: {url}\n")
    print("🔁 Redirection Chain:")
    for i, (u, code) in enumerate(redirs):
        print(f"  {i+1}. {u}  [{code}]")

    print("\n🧠 Final Analysis:")
    print(f"🔹 Original Domain : {domain}")
    print(f"🔹 Original IP     : {ip}")
    print(f"🔹 Final Domain    : {final_domain}")
    print(f"🔹 Final IP        : {final_ip}")
    print(f"🌍 Country         : {country}")
    print(f"💣 Payload Keyword : {keyword if keyword else 'None'}")
    print(f"🦠 VirusTotal      : {'Malicious' if virus_check else 'Clean'}")
    print(f"🚨 Fake            : {'true' if is_fake else 'false'}")

    return {
        "url": url,
        "Domain": domain,
        "IP": ip,
        "Redirections": redirs,
        "Final URL": final_url,
        "Final Domain": final_domain,
        "Final IP": final_ip,
        "Final Country": country,
        "Payload Keyword": keyword,
        "VirusTotal": virus_check,
        "Fake": is_fake
    }
