import subprocess
import socket

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return "N/A"

def traceroute(domain):
    try:
        result = subprocess.check_output(["tracert", domain], shell=True)
        return result.decode()
    except:
        return "Failed traceroute"
