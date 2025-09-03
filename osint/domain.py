import whois
import requests
import socket
import re
import time

HEADERS = {"User-Agent": "tiny-osint-cli/1.0"}

def lookup_domain(domain, retries=3):
    results = []

    # --- WHOIS Info ---
    try:
        w = whois.whois(domain)

        def safe_get(value):
            if isinstance(value, list):
                return ", ".join(str(v) for v in value if v)
            return str(value)

        results.append(("Domain", safe_get(w.domain_name)))
        results.append(("Registrar", safe_get(w.registrar)))
        results.append(("Creation Date", safe_get(w.creation_date)))
        results.append(("Expiration Date", safe_get(w.expiration_date)))
        results.append(("Name Servers", safe_get(w.name_servers)))
        results.append(("Status", safe_get(w.status)))
    except Exception as e:
        results.append(("Whois Error", str(e)))

    # --- Subdomains via crt.sh ---
    subdomains = set()
    for attempt in range(retries):
        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    for entry in data:
                        name = entry.get("name_value")
                        if name:
                            for n in name.split("\n"):
                                n = n.strip().lower()
                                if n.endswith(domain):
                                    subdomains.add(n)
                except ValueError:
                    pass
            break
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
    results.append(("Subdomains", ", ".join(sorted(subdomains)) if subdomains else "None"))

    # --- DNS / IP Resolution ---
    try:
        ip = socket.gethostbyname(domain)
        results.append(("Resolved IP", ip))
    except Exception as e:
        results.append(("DNS Resolution", f"Error: {e}"))

    # --- HTTP Response ---
    try:
        resp = requests.get(f"http://{domain}", headers=HEADERS, timeout=5)
        title_match = re.search(r"<title>(.*?)</title>", resp.text, re.I | re.S)
        title = title_match.group(1).strip() if title_match else "No Title"
        results.append(("HTTP Check", f"{resp.status_code} ({title})"))
    except Exception as e:
        results.append(("HTTP Check Error", str(e)))

    return results
