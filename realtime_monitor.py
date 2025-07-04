import requests, socket
from urllib.parse import urlparse
from ipwhois import IPWhois

def get_ip_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        ip = socket.gethostbyname(domain)
        return domain, ip
    except:
        return None, None

def check_redirection(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)

        redir_list = []
        for resp in r.history:
            redir_list.append((resp.url, resp.status_code))  # 💡 store URL + status code

        # Final destination
        final_url = r.url
        final_code = r.status_code
        redir_list.append((final_url, final_code))

        final_domain = urlparse(final_url).netloc
        final_ip = socket.gethostbyname(final_domain)

        try:
            ip_data = IPWhois(final_ip).lookup_rdap()
            country = ip_data.get("network", {}).get("country", "Unknown")
            org = ip_data.get("network", {}).get("name", "Unknown")
        except:
            country = "Unknown"
            org = "Unknown"

        return redir_list, final_url, final_domain, final_ip, country, org

    except requests.exceptions.RequestException as e:
        print("❌ Error:", str(e))
        return [("[Error] Redirection Failed", "N/A")], "N/A", "N/A", "N/A", "Unknown", "Unknown"

def is_fake_domain(domain):
    with open("data/safe_domains.txt") as f:
        safe = f.read().splitlines()
    return domain not in safe

def analyze_link(url):
    domain, ip = get_ip_domain(url)
    redirs, final_url, final_domain, final_ip, country, org = check_redirection(url)
    fake = is_fake_domain(domain)
    
    # ✅ Print redirection URLs step by step
    print("\n🔁 Redirection Chain:")
    for i, hop in enumerate(redirs):
        print(f"  {i+1}. {hop}")

    return {
        "Domain": domain,
        "IP": ip,
        "Redirections": redirs,
        "Final URL": final_url,
        "Final Domain": final_domain,
        "Final IP": final_ip,
        "Final Country": country,
        "Final Org": org,
        "Fake": fake
    }
    

