import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore
from urllib.parse import urlparse
from requests.exceptions import Timeout, RequestException
import logging

init(autoreset=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_session():
    session = requests.Session()
    session.headers.update(headers) 
    return session

def validate_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and bool(parsed_url.netloc)

def fetch_url(url, session, timeout):
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.content
    except Timeout:
        logging.error(Fore.RED + f"Request timed out for URL: {url}.")
        return None
    except RequestException as e:
        logging.error(Fore.RED + f"Request failed for URL: {url} - {e}.")
        return None

def get_soup(url, session, timeout):
    content = fetch_url(url, session, timeout)
    if content:
        return BeautifulSoup(content, 'html.parser')
    return None

def extract_links(soup):
    return [link.get('href') for link in soup.find_all('a', href=True)] if soup else []

def extract_images(soup):
    return [img.get('src') for img in soup.find_all('img', src=True)] if soup else []

def extract_videos(soup):
    return [video.get('src') for video in soup.find_all('video', src=True)] if soup else []

def extract_scripts(soup):
    scripts_with_src = [script.get('src') for script in soup.find_all('script', src=True)]
    scripts_without_src = [script.string.strip() for script in soup.find_all('script') if script.string and not script.get('src')]
    return scripts_with_src, scripts_without_src

def save_data_to_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for item in data:
                file.write(f"{item}\n")
        logging.info(Fore.GREEN + f"Data saved to {file_path}.")
    except IOError as e:
        logging.error(Fore.RED + f"Failed to save to {file_path}: {e}")

def create_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        logging.info(Fore.GREEN + f"Directory created: {directory}.")
    except OSError as e:
        logging.error(Fore.RED + f"Failed to create directory {directory}: {e}")

def extract_source_code(url, session, output_directory=None, save_to_file=False, timeout=10):
    try:
        content = fetch_url(url, session, timeout)
        if save_to_file and content:
            create_directory(output_directory)
            file_path = os.path.join(output_directory, "source_code.html")
            save_data_to_file([content.decode('utf-8')], file_path)
            logging.info(Fore.GREEN + f"Source code saved in '{file_path}'")
        elif content:
            logging.info(Fore.RED + f"Source code extracted for {url}.")
            print(content.decode('utf-8'))
    except Exception as e:
        logging.error(Fore.RED + f"Failed to extract source code: {e}")

def extract_all(url, session, timeout):
    soup = get_soup(url, session, timeout)
    if not soup:
        return

    scripts_with_src, scripts_without_src = extract_scripts(soup)
    data = {
        "links": extract_links(soup),
        "images": extract_images(soup),
        "videos": extract_videos(soup),
        "scripts_with_src": scripts_with_src,
        "scripts_without_src": scripts_without_src,
    }
    
    output_directory = "pits_found"
    create_directory(output_directory)
    for key, value in data.items():
        if value:
            dir_path = os.path.join(output_directory, key)
            create_directory(dir_path)
            file_path = os.path.join(dir_path, f"{key}_found.txt" if key != "scripts_without_src" else f"{key}_found.js")
            save_data_to_file(value, file_path)
        else:
            logging.warning(Fore.RED + f"No {key} found.")
    
    extract_source_code(url, session, output_directory, save_to_file=True, timeout=timeout)

def display_ascii_art():
    ascii_art = """
    ██████  ██ ████████ ███████  ██████ ██████   █████  ██████  ██    ██ 
    ██   ██ ██    ██    ██      ██      ██   ██ ██   ██ ██   ██  ██  ██  
    ██████  ██    ██    ███████ ██      ██████  ███████ ██████    ████   
    ██      ██    ██         ██ ██      ██   ██ ██   ██ ██         ██    
    ██      ██    ██    ███████  ██████ ██   ██ ██   ██ ██         ██      
    Developed by Pit
    https://github.com/devpit/pitscrapy                                                                         
    """
    print(Fore.GREEN + ascii_art)

def main():
    display_ascii_art()
    session = get_session()

    parser = argparse.ArgumentParser(description="A web scraper to extract links, images, videos, scripts, and source code from a webpage.")
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the webpage to scrape.')

    args = parser.parse_args()
    url = args.url

    if validate_url(url):
        extract_all(url, session, timeout=10)
    else:
        logging.error(Fore.RED + "Invalid URL provided!")

    while True:
        new_url = input(Fore.WHITE + "Do you want to check a new URL? (yes to continue, type 'exit' to quit): ").strip().lower()
        if new_url == 'exit':
            print(Fore.RED + "Exiting the program.")
            break
        elif new_url == 'yes':
            url = input(Fore.WHITE + "Enter the new URL: ").strip()
            if validate_url(url):
                extract_all(url, session, timeout=10)
            else:
                logging.error(Fore.RED + "Invalid URL provided!")
        else:
            logging.error(Fore.RED + "Please type 'yes' to continue or 'exit' to quit.")

if __name__ == '__main__':
    main()
