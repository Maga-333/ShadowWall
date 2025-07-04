import socket
from ipwhois import IPWhois

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return "N/A"

def get_ip_info(ip):
    try:
        obj = IPWhois(ip)
        data = obj.lookup_rdap()
        return {
            "Country": data.get("network", {}).get("country", "Unknown"),
            "Org": data.get("network", {}).get("name", "Unknown"),
            "ASN": data.get("asn", "Unknown")
        }
    except:
        return {
            "Country": "Unknown",
            "Org": "Unknown",
            "ASN": "Unknown"
        }

# Optional: traceroute
def traceroute(domain):
    try:
        import subprocess
        result = subprocess.check_output(["tracert", domain], shell=True)
        return result.decode()
    except:
        return "Traceroute Failed"
