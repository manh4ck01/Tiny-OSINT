# 📌 tiny-osint

A lightweight **Open Source Intelligence (OSINT) CLI tool** written in Python.
It allows you to quickly perform reconnaissance on various identifiers such as **IP addresses, domains, emails, usernames, and phone numbers** — directly from your terminal.

---

## ✨ Features

* 🔎 **Scan mode (`scan`)**

  * Detects the type of query automatically:

    * **IP address** → Geolocation lookup
    * **Domain** → WHOIS & domain info
    * **Email** → (placeholder, breach check requires API key)
    * **Phone number** → Basic phone info lookup
    * **Username** → Check availability across platforms

* 📞 **Phone mode (`phone`)**

  * Advanced phone number lookup using [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers):

    * E.164, International, and National formats
    * Validation (valid/invalid, possible/impossible)
    * Region and carrier information
    * Number type (Mobile, Fixed Line, VoIP, etc.)
    * Timezones for the number

* 📂 **Batch Scanning**

  * Provide a file with multiple targets (one per line) using `--file`

* 🖥️ **Pretty CLI Output**

  * Results formatted into clean, human-readable tables
  * JSON output supported for advanced phone lookups

---

## 🚀 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/manh4ck01/tiny-osint.git
   cd tiny-osint
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the environment:

   * **Git Bash / Linux / macOS**:

     ```bash
     source venv/bin/activate
     ```
   * **Windows (PowerShell)**:

     ```powershell
     venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD)**:

     ```cmd
     venv\Scripts\activate
     ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Usage

### General Scan

```bash
python cli.py scan <target>
```

**Examples:**

```bash
python cli.py scan example.com      # Domain lookup
python cli.py scan 8.8.8.8          # IP geolocation
python cli.py scan "+14155552671"   # Phone lookup
python cli.py scan johndoe          # Username check
python cli.py scan user@example.com # Email lookup (stub)
```

### Batch Scan (targets from file)

```bash
python cli.py scan --file targets.txt
```

`targets.txt` should contain one target per line:

```
example.com
8.8.8.8
+14155552671
johndoe
user@example.com
```

### Advanced Phone Lookup

```bash
python cli.py phone <number> [options]
```

**Examples:**

```bash
python cli.py phone "+14155552671"
python cli.py phone "+14155552671" -r US
python cli.py phone "+14155552671" -j   # JSON output
```

---

## 📦 Dependencies

* [phonenumbers](https://pypi.org/project/phonenumbers/)
* [requests](https://pypi.org/project/requests/)
* [argparse](https://docs.python.org/3/library/argparse.html) (stdlib)
* [json](https://docs.python.org/3/library/json.html) (stdlib)

---

## ⚠️ Notes

* **Email breach lookup** is currently disabled (requires an API key for services like HaveIBeenPwned).
* Ensure you **do not name files after Python standard libraries** (e.g., `email.py`, `json.py`) to avoid import conflicts.
* This project is for **educational and research purposes only**. Please use responsibly.

---

## 📝 Roadmap

* [ ] Enable email breach lookup (via API key integration)
* [ ] Expand domain info (DNS records, SSL, subdomains)
* [ ] Add social media OSINT modules
* [ ] Export results to CSV/JSON

---

## 📜 License

MIT License © 2025 — Makhosi Andile Surge
