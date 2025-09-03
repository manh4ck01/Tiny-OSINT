import requests

HIBP_API = "https://haveibeenpwned.com/api/v3/breachedaccount/{}"
# You need an API key from HIBP; for now we’ll do a basic version without authentication (rate-limited)

HEADERS = {
    "User-Agent": "tiny-osint-tool",
    # If you have an API key, uncomment below
    # "hibp-api-key": "YOUR_API_KEY_HERE"
}

def check_email(email):
    try:
        response = requests.get(HIBP_API.format(email), headers=HEADERS, timeout=10)
        if response.status_code == 200:
            breaches = response.json()
            results = [f"Breaches found for {email}:"]
            for breach in breaches:
                results.append(f"- {breach['Name']} ({breach['BreachDate']})")
            return "\n".join(results)
        elif response.status_code == 404:
            return f"No breaches found for {email} ✅"
        else:
            return f"Error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Exception occurred: {e}"
