
# PitScrapy - Massive Data Collection

PitScrapy is a powerful Python tool for collecting data from web pages quickly and efficiently. With it, you can extract links, images, videos, scripts, and the source code from any web page. Ideal for developers and students.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [How to Use](#how-to-use)
  - [Syntax](#syntax)
  - [Usage Examples](#usage-examples)
- [Why Use PitScrapy?](#why-use-pitscrapy)
- [Contribution](#contribution)
- [Support](#support)
- [Legal and Ethical Considerations](#legal-and-ethical-considerations)

## Features

- `-u`, `--url`: Target URL (mandatory)
- `-l`, `--links`: Extract links
- `-i`, `--images`: Extract images
- `-v`, `--videos`: Extract videos
- `-sc`, `--source-code`: Display the page's source code
- `-scs`, `--source-code-save`: Save the page's source code to a file
- `-sws`, `--scripts-with-src`: Extract scripts with `src` attribute
- `-swss`, `--scripts-without-src`: Extract scripts without `src` attribute
- `-all`, `--all`: Extract all data at once
- `-h`, `--help`: Show this help message

## Installation

Before starting, install the following libraries:

```bash
pip install requests beautifulsoup4 colorama
```
Or, if you prefer, install using the requirements file:

```bash
pip install -r requirements.txt
```

## How to Use

### Syntax

```bash
python pitscrapy.py -u <URL> [options]
```

### Usage Examples

1. **Extract links from a page:**
    ```bash
    python pitscrapy.py -u http://example.com -l
    ```

2. **Extract images and videos from a page:**
    ```bash
    python pitscrapy.py -u http://example.com -i -v
    ```

3. **Save the page's source code to a file:**
    ```bash
    python pitscrapy.py -u http://example.com -scs
    ```

4. **Extract all data at once:**
    ```bash
    python pitscrapy.py -u http://example.com -all
    ```

## Why Use PitScrapy?

### Simplicity and Efficiency

PitScrapy was developed to be simple to use and efficient in data collection. With just a few commands, you can quickly obtain all the data from a web page.

### Task Automation

PitScrapy allows you to automate web data collection, saving time and effort. It is ideal for projects that require regular data collection from multiple pages.

### Content Analysis

The extracted data can be used for detailed analysis, such as checking the frequency of certain content types or analyzing the source code to better understand the structure of a web page.

### Education and Research

For students and researchers, PitScrapy is a valuable tool for learning about web scraping and data analysis. Use the collected data for research projects, case studies, or to better understand how web pages are built.

## Support

If you encounter issues or have questions, feel free to open an issue on [GitHub](https://github.com/devpit/pitscrapy/issues).

## Legal and Ethical Considerations

PitScrapy is a tool for web data collection and should be used in accordance with the terms of service and applicable laws of each website. **We do not take responsibility for the improper or illegal use of the tool.**

Ensure that you use PitScrapy ethically and legally. Respect the terms of service of the websites you access and avoid overloading servers with excessive requests.
