import requests, re, random, time, json, csv, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate

HEADERS = {"User-Agent": "tiny-osint-cli/1.0"}

# --- Platform list (with categories & optional validation regex) ---
PLATFORMS = {
    # Social
    "Twitter": {"url": "https://twitter.com/{}", "category": "Social", "validate": r"@{}"},
    "Instagram": {"url": "https://www.instagram.com/{}", "category": "Social"},
    "Facebook": {"url": "https://www.facebook.com/{}", "category": "Social", "validate": r"facebook.com/{}"},
    "TikTok": {"url": "https://www.tiktok.com/@{}", "category": "Social"},
    "Snapchat": {"url": "https://www.snapchat.com/add/{}", "category": "Social"},
    "Pinterest": {"url": "https://www.pinterest.com/{}", "category": "Social"},
    "VK": {"url": "https://vk.com/{}", "category": "Social"},
    "Mastodon": {"url": "https://mastodon.social/@{}", "category": "Social"},
    "Reddit": {"url": "https://www.reddit.com/user/{}", "category": "Forums"},
    "Quora": {"url": "https://www.quora.com/profile/{}", "category": "Forums"},
    "HackerNews": {"url": "https://news.ycombinator.com/user?id={}", "category": "Forums"},
    "MyAnimeList": {"url": "https://myanimelist.net/profile/{}", "category": "Forums"},

    # Developer
    "GitHub": {"url": "https://github.com/{}", "category": "Developer", "validate": r"<title>(.*?) · GitHub</title>"},
    "GitLab": {"url": "https://gitlab.com/{}", "category": "Developer"},
    "Bitbucket": {"url": "https://bitbucket.org/{}", "category": "Developer"},
    "StackOverflow": {"url": "https://stackoverflow.com/users/{}", "category": "Developer"},
    "CodePen": {"url": "https://codepen.io/{}", "category": "Developer"},
    "Replit": {"url": "https://replit.com/@{}", "category": "Developer"},
    "DevTo": {"url": "https://dev.to/{}", "category": "Developer"},

    # Media / Music
    "YouTube": {"url": "https://www.youtube.com/{}", "category": "Media"},
    "Twitch": {"url": "https://www.twitch.tv/{}", "category": "Media"},
    "Vimeo": {"url": "https://vimeo.com/{}", "category": "Media"},
    "Flickr": {"url": "https://www.flickr.com/people/{}", "category": "Media"},
    "SoundCloud": {"url": "https://soundcloud.com/{}", "category": "Music"},
    "Spotify": {"url": "https://open.spotify.com/user/{}", "category": "Music"},
    "Mixcloud": {"url": "https://www.mixcloud.com/{}", "category": "Music"},

    # Professional
    "LinkedIn": {"url": "https://www.linkedin.com/in/{}", "category": "Professional"},
    "Xing": {"url": "https://www.xing.com/profile/{}", "category": "Professional"},
    "AngelList": {"url": "https://angel.co/u/{}", "category": "Professional"},

    # Blogs
    "Medium": {"url": "https://medium.com/@{}", "category": "Blogs"},
    "Tumblr": {"url": "https://{}.tumblr.com", "category": "Blogs"},
    "Blogger": {"url": "https://{}.blogspot.com", "category": "Blogs"},

    # Misc / Funding
    "Patreon": {"url": "https://www.patreon.com/{}", "category": "Support"},
    "Kickstarter": {"url": "https://www.kickstarter.com/profile/{}", "category": "Funding"},
    "BuyMeACoffee": {"url": "https://www.buymeacoffee.com/{}", "category": "Support"},
}


# --- Username detectors ---
def detect_username_type(username):
    if "@" in username:
        return "Email-style"
    elif username.isdigit():
        return "Numeric"
    elif re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Alphanumeric"
    else:
        return "Special chars / complex"


def detect_length_category(username):
    length = len(username)
    if length <= 4:
        return "Very short"
    elif length <= 8:
        return "Short"
    elif length <= 15:
        return "Medium"
    else:
        return "Long"


def detect_real_name(username):
    if username.isalpha() and 2 <= len(username) <= 12:
        return "Likely real name"
    return "Unknown / handle"


def detect_bot(username):
    patterns = ["bot", "test", "admin", "auto", "fake"]
    if any(pat in username.lower() for pat in patterns):
        return "Possible bot"
    return "No"


def detect_disposable_email(username):
    if "@" in username:
        disposable_domains = ["mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com"]
        domain = username.split("@")[-1].lower()
        if domain in disposable_domains:
            return "Disposable email"
        return "Not disposable"
    return "N/A"


# --- Platform check ---
def check_platform(name, config, username, proxies=None, retries=3):
    url = config["url"].format(username)
    category = config.get("category", "Other")
    validate = config.get("validate")

    proxy = None
    if proxies:
        choice = random.choice(proxies)
        proxy = {"http": choice, "https": choice}

    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=7, proxies=proxy)
            if resp.status_code == 200:
                if validate:
                    if re.search(validate.format(username), resp.text, re.I):
                        return category, name, "✅ exists"
                    else:
                        return category, name, "❓ maybe exists (validation failed)"
                return category, name, "✅ exists"
            elif resp.status_code == 404:
                return category, name, "❌ does NOT exist"
            else:
                return category, name, f"⚠ {resp.status_code}"
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            return category, name, f"⚠ error ({e})"


# --- Main scan ---
def check_username(username, threads=10, proxies=None, retries=3):
    results = []

    # Add detectors
    results.append(("Meta", "Detected Type", detect_username_type(username)))
    results.append(("Meta", "Length Category", detect_length_category(username)))
    results.append(("Meta", "Length", len(username)))
    results.append(("Meta", "Real Name Detection", detect_real_name(username)))
    results.append(("Meta", "Bot Detection", detect_bot(username)))
    results.append(("Meta", "Disposable Email", detect_disposable_email(username)))

    # Parallel platform checking
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_platform, platform, cfg, username, proxies, retries): platform
            for platform, cfg in PLATFORMS.items()
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return results


# --- Export ---
def export_results(results, fmt, filename):
    if fmt == "json":
        data = [{"category": c, "platform": p, "status": s} for c, p, s in results]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Platform", "Status"])
            writer.writerows(results)
    elif fmt == "md":
        table = tabulate(results, headers=["Category", "Platform", "Status"], tablefmt="github")
        with open(filename, "w") as f:
            f.write(table)


# --- CLI ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tiny OSINT Username Scanner")
    parser.add_argument("username", help="Username or handle to scan")
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent threads")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries on error/timeout")
    parser.add_argument("--export", choices=["json", "csv", "md"], help="Export format")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--proxies", help="File with proxy list")
    args = parser.parse_args()

    proxy_list = None
    if args.proxies:
        with open(args.proxies) as f:
            proxy_list = [line.strip() for line in f if line.strip()]

    results = check_username(args.username, threads=args.threads, proxies=proxy_list, retries=args.retries)

    print(tabulate(results, headers=["Category", "Platform", "Status"], tablefmt="grid"))

    if args.export and args.output:
        export_results(results, args.export, args.output)
        print(f"\n✅ Results exported to {args.output}")
