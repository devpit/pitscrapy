<div align="center">

# 🕷️ PitScrapy

**A Python web scraper for extracting and organizing information from HTML pages.**

**Version 2.0.0** · **Python 3.10+** · **Interactive terminal interface**

[Installation](#-installation) • [Usage](#-usage) • [Extracted Data](#-what-pitscrapy-extracts) • [Output Files](#-output-files) • [CLI Options](#️-command-line-options)

</div>

---

## 📖 Overview

**PitScrapy** is a Python-based web scraping tool designed to collect and organize information available in a web page's HTML.

Built with **Rich** for a user-friendly terminal experience, it can scan a URL, display a summary of the page, let you browse the extracted data, and export results to **JSON**, **TXT**, **HTML**, and **JS** files.

You can use PitScrapy in **interactive mode** with a terminal menu or in **command-line mode** to scan a page with a single command.

> **Note:** PitScrapy analyzes the HTML returned by the requested page. It does not crawl an entire website, execute client-side JavaScript in a browser, or download the media files it discovers.

## ✨ Features

- 🔎 Extracts information from **HTTP and HTTPS** pages.
- 🌐 Accepts URLs with or without `https://` (HTTPS is added automatically when no scheme is provided).
- 📋 Displays the page title, final URL, HTTP status, HTML size, and description when available.
- 🧭 Converts relative resource URLs into absolute URLs and removes URL fragments (`#...`).
- 🧹 Removes duplicate entries while preserving their original order.
- 🖼️ Discovers links to images, videos, stylesheets, scripts, and iframes.
- 📩 Extracts email addresses from `mailto:` links and phone numbers from `tel:` links.
- 📑 Collects form methods and actions, headings, and meta tags.
- 💾 Exports the downloaded HTML and structured scan results.
- 🛡️ Supports optional `robots.txt` checks before scanning.
- ⚙️ Lets you configure request timeout, maximum HTML size, output folder, and file saving.
- 🔁 Retries eligible GET requests up to **two times** for HTTP `429`, `500`, `502`, `503`, and `504` responses.
- 🎨 Uses styled menus, tables, and status messages in the terminal.

## 📦 What PitScrapy Extracts

| Category | Extracted information |
|---|---|
| `links` | URLs found in `<a href>` elements |
| `images` | Image URLs from `src`, `data-src`, `data-lazy-src`, and `srcset` |
| `videos` | Video URLs from `<video src>` and `<video><source src>` |
| `external_scripts` | URLs from external `<script src>` elements |
| `inline_scripts` | JavaScript content from `<script>` elements without `src` |
| `stylesheets` | CSS URLs from `<link rel="stylesheet">` elements |
| `iframes` | Embedded content URLs from `<iframe src>` |
| `emails` | Email addresses found in `mailto:` links |
| `phones` | Phone values found in `tel:` links |
| `forms` | HTTP methods and destination URLs of forms |
| `headings` | Text from `h1`, `h2`, and `h3` elements |
| `meta_tags` | Meta tags with a `content` value and a `name`, `property`, or `http-equiv` attribute |

The structured results also include the requested URL, final URL after redirects, HTTP status code, content type, downloaded byte count, page title, description, canonical URL, and item counts for every category.

## 🚀 Installation

### Prerequisites

- **Python 3.10** or newer
- **pip**
- An internet connection to access the target website

### 1. Clone the repository

```bash
git clone https://github.com/devpit/pitscrapy.git
cd pitscrapy
```

Alternatively, download the project files and extract them into a folder.

### 2. Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

From the project directory, run:

```bash
pip install -r requirements.txt
```

This installs the Python packages required by PitScrapy. Make sure the `requirements.txt` file is in the project directory before running the command.

> The commands below assume the main script is named `pitscrapy.py`. If your file has a different name, update the commands accordingly.

## 💻 Usage

### Interactive mode

Launch PitScrapy without arguments:

```bash
python pitscrapy.py
```

The main menu looks like this:

```text
MAIN MENU
[1] Scan URL
[2] Browse last scan
[3] Settings
[4] Exit
```

**Menu options:**

1. **Scan URL** — Enter a website URL, run a scan, and display the results.
2. **Browse last scan** — Browse the extracted categories from the most recent successful scan in the current session.
3. **Settings** — Change the request timeout, maximum HTML size, output directory, file saving, and `robots.txt` checks.
4. **Exit** — Close the application.

### Command-line mode

Scan a page without opening the interactive menu:

```bash
python pitscrapy.py --url https://example.com
```

The protocol is optional:

```bash
python pitscrapy.py -u example.com
```

### Command examples

**Scan a page and choose an output folder:**

```bash
python pitscrapy.py -u https://example.com -o my_results
```

**Scan a page without saving files:**

```bash
python pitscrapy.py -u https://example.com --no-save
```

**Set a 30-second timeout and a 20 MB HTML size limit:**

```bash
python pitscrapy.py -u https://example.com --timeout 30 --max-size-mb 20
```

**Check `robots.txt` before scanning:**

```bash
python pitscrapy.py -u https://example.com --respect-robots
```

**Display the installed version:**

```bash
python pitscrapy.py --version
```

**Show command-line help:**

```bash
python pitscrapy.py --help
```

## ⚙️ Command-Line Options

| Option | Description | Default |
|---|---|---|
| `-u`, `--url` | URL to scan; starts interactive mode if omitted | Interactive mode |
| `-o`, `--output` | Directory for exported results | `pitscrapy_results` |
| `--timeout` | Request timeout in seconds | `15` |
| `--max-size-mb` | Maximum HTML response size in MB | `10` |
| `--no-save` | Show results without saving files | Saving enabled |
| `--respect-robots` | Check `robots.txt` before requesting the page | Disabled |
| `--no-robots` | Explicitly skip `robots.txt` checks | Default behavior |
| `--version` | Display the PitScrapy version | — |
| `-h`, `--help` | Display the help message | — |

`--respect-robots` and `--no-robots` cannot be used together.

## 📁 Output Files

When saving is enabled, every scan creates its own directory named after the website hostname and a UTC timestamp. By default, these directories are created inside `pitscrapy_results`.

**Example output structure:**

```text
pitscrapy_results/
└── example.com_20261011_153000_123456Z/
    ├── source_code.html
    ├── results.json
    ├── links.txt
    ├── images.txt
    ├── videos.txt
    ├── external_scripts.txt
    ├── inline_scripts.js
    ├── stylesheets.txt
    ├── iframes.txt
    ├── emails.txt
    ├── phones.txt
    ├── forms.txt
    ├── headings.txt
    └── meta_tags.txt
```

> Category-specific `.txt` and `.js` files are created **only when that category contains results**. `source_code.html` and `results.json` are always written when saving succeeds.

| File | Contents |
|---|---|
| `source_code.html` | Original HTML downloaded from the page |
| `results.json` | Scan metadata, item counts, and extracted data in JSON format |
| `links.txt`, `images.txt`, etc. | One extracted entry per line for each populated category |
| `inline_scripts.js` | Extracted inline scripts, separated by comments |

### Example `results.json`

```json
{
  "requested_url": "https://example.com",
  "final_url": "https://example.com",
  "status_code": 200,
  "content_type": "text/html",
  "bytes_downloaded": 1256,
  "title": "Example Domain",
  "description": "",
  "canonical_url": "",
  "counts": {
    "links": 1,
    "images": 0
  },
  "data": {
    "links": ["https://www.iana.org/domains/example"],
    "images": []
  }
}
```

> This is an **illustrative, shortened example**. Actual JSON output includes all supported categories and their counts, even when empty. Values depend on the page being scanned.

## 🔧 How It Works

1. **URL validation:** Normalizes the target URL and accepts only HTTP or HTTPS URLs without embedded credentials.
2. **Optional robots check:** When `--respect-robots` is enabled, checks the requested page against its site's `robots.txt` file.
3. **HTTP request:** Uses a `requests.Session` with a custom User-Agent, redirects enabled, and an HTTP retry policy.
4. **Response size protection:** Reads the response in chunks and stops if the configured size limit is exceeded.
5. **HTML extraction:** Uses **Beautiful Soup** to identify and categorize information from the downloaded document.
6. **Terminal summary:** Displays scan details, category counts, and previews of links, images, videos, and external scripts.
7. **Export:** Saves the HTML, JSON summary, and populated category files when enabled.

## ⚠️ Limitations and Responsible Use

- **Single-page scans:** PitScrapy is not a recursive crawler. It lists discovered links without visiting them automatically.
- **No JavaScript rendering:** Content inserted by JavaScript after a browser loads the page may not be present in the downloaded HTML.
- **No asset downloads:** Image, video, CSS, and external script URLs are collected, but the files themselves are not downloaded.
- **HTML-dependent extraction:** Email addresses and phone numbers are found through `mailto:` and `tel:` links, not through arbitrary text recognition.
- **Website restrictions:** Some websites require authentication, restrict automated requests, or enforce rate limits. PitScrapy does not bypass CAPTCHAs or access restrictions.
- **Responsible scraping:** Follow the website's terms, access permissions, applicable privacy laws, and rate limits. Use `--respect-robots` to enable `robots.txt` checking; it is **disabled by default** in this version.

## 🛠️ Tech Stack

- **Python** — Core programming language
- **Requests** — HTTP requests and session management
- **Beautiful Soup 4** — HTML parsing and data extraction
- **Rich** — Terminal interface, tables, and status messages
- **urllib3** — HTTP retry configuration
- **argparse** — Command-line argument parsing (Python standard library)

## 👨‍💻 Author

**Developed by Pit**

Project repository: [github.com/devpit/pitscrapy](https://github.com/devpit/pitscrapy)

---

<div align="center">

**PitScrapy 2.0.0 — Simple, organized HTML information extraction.**

</div>
