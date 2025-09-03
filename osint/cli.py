import argparse
import json
import re
from osint import username, ip, domain, email_lookup as email, phone
from osint.utils import print_table
from phone_lookup import lookup_phone
from osint import email_lookup as email


def scan(query):
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    domain_pattern = r"^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    phone_pattern = r"^\+?\d[\d\s\-]{7,}\d$"

    if re.match(ip_pattern, query):
        data = ip.lookup_ip(query)
        print_table(f"IP Geolocation: {query}", data)
    elif re.match(domain_pattern, query):
        data = domain.lookup_domain(query)
        print_table(f"Domain Lookup: {query}", data)
    elif re.match(email_pattern, query):
        print(f"[+] Email breach check disabled (API key required)")
    elif re.match(phone_pattern, query):
        data = phone.lookup_phone(query)
        print_table(f"Phone Lookup: {query}", data)
    else:
        data = username.check_username(query)
        print_table(f"Username Check: {query}", data)


def cli():
    parser = argparse.ArgumentParser(
        prog="tiny-osint",
        description="A lightweight CLI OSINT tool"
    )
    subparsers = parser.add_subparsers(dest="command")

    # ----------------------------
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Run a generic OSINT scan")
    scan_parser.add_argument("query", nargs="?", help="Target to scan (username, domain, IP, email, phone)")
    scan_parser.add_argument("--file", "-f", help="File with list of targets, one per line")

    # ----------------------------
    # phone command
    phone_parser = subparsers.add_parser("phone", help="Run advanced phone number lookups")
    phone_parser.add_argument("numbers", nargs="+", help="Phone numbers to look up")
    phone_parser.add_argument("-r", "--region", help="Default region (e.g., US, GB, IN)", default=None)
    phone_parser.add_argument("-j", "--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if args.command == "scan":
        if args.file:
            try:
                with open(args.file, "r") as f:
                    targets = [line.strip() for line in f if line.strip()]
                for target in targets:
                    print(f"\n🔍 Scanning: {target}")
                    scan(target)
            except Exception as e:
                print(f"Error reading file: {e}")
        elif args.query:
            scan(args.query)
        else:
            print("Error: Provide a query or --file")

    elif args.command == "phone":
        results = []
        for num in args.numbers:
            results.append((num, lookup_phone(num, args.region)))

        if args.json:
            print(json.dumps(dict(results), indent=2))
        else:
            for num, data in results:
                print(f"\n📞 Lookup for: {num}")
                if "error" in data:
                    print(f"  Error: {data['error']}")
                    continue
                print(f"  E.164 format     : {data['formats']['e164']}")
                print(f"  International    : {data['formats']['international']}")
                print(f"  National         : {data['formats']['national']}")
                print(f"  Valid            : {'Yes' if data['valid'] else 'No'}")
                print(f"  Possible         : {'Yes' if data['possible'] else 'No'}")
                print(f"  Region           : {data['region']}")
                print(f"  Carrier          : {data['carrier']}")
                print(f"  Type             : {data['type']}")
                print(f"  Timezones        : {', '.join(data['timezones'])}")

    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
