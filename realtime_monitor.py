from utils.url_analyzer import analyze_link

def analyze_and_format(url):
    try:
        result = analyze_link(url)

        domain = result.get("Domain", "N/A")
        ip = result.get("IP", "N/A")
        redirs = result.get("Redirections", [])
        fake = result.get("Fake", False)

        # Determine status
        if domain == "N/A" or ip == "N/A":
            status = "UNKNOWN"
        elif fake:
            status = "DANGER"
        else:
            status = "SAFE"

        return {
            "Domain": domain,
            "IP": ip,
            "Redirections": redirs,
            "Status": status
        }

    except Exception as e:
        return {
            "Error": str(e)
        }
