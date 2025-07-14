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

# ✅ Redirection + WHOIS
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
    return False

# ✅ Main Analyzer Function
def analyze_link(url):
    safe_list, danger_list, payload_keywords = load_domain_lists()

    reasons = []
    redirection_error = False
    virus_check = virustotal_check(url)
    ip_flagged = False  # Placeholder; can be extended later

    domain, ip = get_ip_domain(url)
    redirs, final_url, final_domain, final_ip, country, org = check_redirection(url)

    if redirs == [("[Error] Redirection Failed", "N/A")]:
        redirection_error = True
        redirs = [[url, 0]]
        final_url = url
        final_domain = domain
        final_ip = ip
        country = "Unknown"
        org = "Unknown"
        reasons.append("Redirection failed")

    domain = domain.lower() if domain else "unknown"
    final_domain = final_domain.lower() if final_domain else "unknown"

    keyword = has_payload_keyword(url, payload_keywords)
    if keyword:
        reasons.append(f"Payload keyword: {keyword}")

    in_danger = domain in danger_list or final_domain in danger_list
    if in_danger:
        reasons.append("Domain listed in danger_domains.txt")

    in_safe = domain in safe_list or final_domain in safe_list
    if in_safe:
        reasons.clear()  # No need to mark as fake if safe

    multiple_redirections = len(redirs) > 1
    if multiple_redirections:
        reasons.append("Multiple redirections")

    is_fake = (
        not in_safe and (
            in_danger or
            keyword is not None or
            virus_check or
            multiple_redirections or
            redirection_error
        )
    )

    formatted_redirs = [[u, code] for u, code in redirs]

    result = {
        "url": url,
        "Domain": domain,
        "IP": ip,
        "Redirections": formatted_redirs,
        "Final URL": final_url,
        "Final Domain": final_domain,
        "Final IP": final_ip,
        "Final Country": country,
        "Payload Keyword": keyword,
        "IP Flagged": ip_flagged,
        "Redirection Error": redirection_error,
        "Fake": is_fake,
        "Reasons": reasons
    }

    # 🖨 Pretty print
    print("\n📄 Detailed Report:")
    for k, v in result.items():
        print(f"{k:>18}: {v}")

    return result

# 🧪 Test (example)
if __name__ == "__main__":
    analyze_link("https://americannews.com/")
