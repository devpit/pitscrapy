# PitScrapy - Powerful Web Data Scraping Tool

PitScrapy is a Python-based web scraper designed to efficiently collect a variety of data from web pages, including links, images, videos, scripts, and source code. Ideal for developers, researchers, and students looking to automate data extraction from websites.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Syntax](#syntax)
  - [Examples](#examples)
- [Why Choose PitScrapy?](#why-choose-pitscrapy)
- [Contribution](#contribution)
- [Support](#support)
- [Legal and Ethical Considerations](#legal-and-ethical-considerations)

## Features

- Extract various types of data:
  - **Links**: All URLs from `<a>` tags.
  - **Images**: URLs of images from `<img>` tags.
  - **Videos**: URLs of videos from `<video>` tags.
  - **Scripts**: Scripts with and without `src` attributes.
  - **Source Code**: View and optionally save the page's full HTML.
- Save extracted data into organized folders for easy access.
- Automatically handles timeouts and errors gracefully, with log output for debugging.

## Installation

Before using PitScrapy, install the required libraries:

```bash
pip install requests beautifulsoup4 colorama
```

Or, install dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Usage

### Syntax

Run PitScrapy with the following command:

```bash
python pitscrapy.py -u <URL>
```

### Examples

1. **Extract all data types from a page and save to files:**
    ```bash
    python pitscrapy.py -u http://example.com
    ```

## Why Choose PitScrapy?

### Ease of Use and Flexibility

PitScrapy is straightforward and can be run with simple commands. Easily tailor it to collect specific data types as needed.

### Efficient Automation

Ideal for repetitive data collection from multiple sites, helping automate research and development workflows.

### Versatile Application

Whether for educational use, data analysis, or content auditing, PitScrapy supports various needs with customizable output.

## Contribution

Contributions are welcome! Feel free to fork the project, submit pull requests, or report issues on [GitHub](https://github.com/devpit/pitscrapy/issues).

## Support

For questions or troubleshooting, check the issues section on GitHub or start a new issue.

## Legal and Ethical Considerations

PitScrapy is a tool for collecting publicly available data. Users are responsible for ensuring their actions comply with the terms of service of each website and relevant laws. Use this tool ethically, avoid excessive requests, and respect site policies.
