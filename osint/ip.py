import requests

def lookup_ip(ip_address):
    try:
        # Example using ip-api.com
        url = f"http://ip-api.com/json/{ip_address}"
        data = requests.get(url).json()
        if data["status"] == "success":
            return [
                ("IP", data["query"]),
                ("Country", data["country"]),
                ("Region", data["regionName"]),
                ("City", data["city"]),
                ("ISP", data["isp"]),
                ("Lat/Lon", f"{data['lat']}, {data['lon']}")
            ]
        else:
            return [("Error", data.get("message", "Unknown"))]
    except Exception as e:
        return [("Error", str(e))]
