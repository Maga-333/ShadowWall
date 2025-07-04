import requests, re, socket
from urllib.parse import urlparse
import subprocess

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
r = requests.get(url, timeout=3, allow_redirects=True)
hops = [resp.url for resp in r.history] + [r.url]
return hops
except:
return ["[Error] Redirection Failed"]

def is_fake_domain(domain):
with open("data/safe_domains.txt") as f:
safe = f.read().splitlines()
return domain not in safe

def analyze_link(url):
domain, ip = get_ip_domain(url)
redirs = check_redirection(url)
fake = is_fake_domain(domain)
return {
"Domain": domain,
"IP": ip,
"Redirections": redirs,
"Fake": fake
}

