import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore

init(autoreset=True)

def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Request failed: {e}")
        return None

def extract_links(soup):
    return [link.get('href') for link in soup.find_all('a', href=True)] if soup else []

def extract_images(soup):
    return [img.get('src') for img in soup.find_all('img', src=True)] if soup else []

def extract_videos(soup):
    return [video.get('src') for video in soup.find_all('video', src=True)] if soup else []

def extract_scripts(soup):
    if soup:
        scripts_with_src = [script.get('src') for script in soup.find_all('script', src=True)]
        scripts_without_src = [script.string.strip() for script in soup.find_all('script') if script.string and not script.get('src')]
        return scripts_with_src, scripts_without_src
    return [], []

def save_to_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write("%s\n" % item)

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_source_code(url, output_directory=None, save_to_file=False):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        if save_to_file:
            create_directory(output_directory)
            file_path = os.path.join(output_directory, "source_code.html")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            print(Fore.GREEN + f"Source code saved in '{file_path}'")
        else:
            print(Fore.GREEN + content)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Request failed: {e}")

def extract_all(url):
    soup = get_soup(url)
    if not soup:
        return

    data = {
        "links": extract_links(soup),
        "images": extract_images(soup),
        "videos": extract_videos(soup),
        "scripts_with_src": extract_scripts(soup)[0],
        "scripts_without_src": extract_scripts(soup)[1],
    }
    
    output_directory = "data_found"
    create_directory(output_directory)
    for key, value in data.items():
        if value:
            dir_path = os.path.join(output_directory, key)
            create_directory(dir_path)
            file_path = os.path.join(dir_path, f"{key}_found.txt" if key != "scripts_without_src" else f"{key}_found.js")
            save_to_file(value, file_path)
            print(Fore.GREEN + f"{key.capitalize()} saved in: {file_path}")
        else:
            print(Fore.RED + f"No {key} found.")
    extract_source_code(url, output_directory, save_to_file=True)

def display_help():
    help_text = """  
    Pit Scrapy | Massive Data Colect - Usage:
    - Enter the target URL when prompted.
    - Choose what you want to extract:
        -l : Extract links
        -i : Extract images
        -v : Extract videos
        -sc : Extract source code and display it
        -scs : Extract source code and save to file
        -sws : Extract scripts with src attribute
        -swss : Extract scripts without src attribute
        -all : Extract everything at once
        
    Example:
    pitscrapy.py -u http://example.com -l -i -v

    Credits:
    Developed by the DevPit
    https://github.com/devpit/pitscrapy
    """
    print(help_text)

def display_ascii_art():
    ascii_art = """
    #####    ######   ######    ####     ####    #####      ##     #####    ##  ##
    ##  ##     ##       ##     ##       ##  ##   ##  ##    ####    ##  ##   ##  ##
    ##  ##     ##       ##      ####    ##       ##  ##   ##  ##   ##  ##    ####
    #####      ##       ##         ##   ##       #####    ##  ##   #####      ##
    ##         ##       ##         ##   ##  ##   ## ##    ######   ##         ##
    ##       ######     ##      ####     ####    ##  ##   ##  ##   ##         ##                          
    """
    print(Fore.GREEN + ascii_art)

def main():
    parser = argparse.ArgumentParser(description="Pit Scrapy - Massive Data Colect", add_help=False)
    parser.add_argument('-u', '--url', required=False, help='Target URL')
    parser.add_argument('-l', '--links', action='store_true', help='Extract links')
    parser.add_argument('-i', '--images', action='store_true', help='Extract images')
    parser.add_argument('-v', '--videos', action='store_true', help='Extract videos')
    parser.add_argument('-sc', '--source-code', action='store_true', help='Extract and display source code')
    parser.add_argument('-scs', '--source-code-save', action='store_true', help='Extract and save source code to file')
    parser.add_argument('-sws', '--scripts-with-src', action='store_true', help='Extract scripts with src attribute')
    parser.add_argument('-swss', '--scripts-without-src', action='store_true', help='Extract scripts without src attribute')
    parser.add_argument('-all', '--all', action='store_true', help='Extract everything at once')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')

    args = parser.parse_args()

    if args.help:
        display_ascii_art()
        display_help()
        sys.exit(0)

    if not args.url:
        print(Fore.RED + "No URL provided!")
        display_ascii_art()
        display_help()
        sys.exit(1)

    display_ascii_art()

    if not (args.links or args.images or args.videos or args.source_code or args.source_code_save or args.scripts_with_src or args.scripts_without_src or args.all):
        print(Fore.RED + "No extraction option was provided!")
        display_help()
        sys.exit(1)

    url = args.url
    soup = get_soup(url)

    if args.all:
        extract_all(url)
    else:
        if args.links:
            links = extract_links(soup)
            if links:
                create_directory("links")
                save_to_file(links, "links/links_found.txt")
                print(Fore.GREEN + "Links saved in 'links/links_found.txt'")
            else:
                print(Fore.RED + "No links found.")
        
        if args.images:
            images = extract_images(soup)
            if images:
                create_directory("images")
                save_to_file(images, "images/images_found.txt")
                print(Fore.GREEN + "Images saved in 'images/images_found.txt'")
            else:
                print(Fore.RED + "No images found.")
        
        if args.videos:
            videos = extract_videos(soup)
            if videos:
                create_directory("videos")
                save_to_file(videos, "videos/videos_found.txt")
                print(Fore.GREEN + "Videos saved in 'videos/videos_found.txt'")
            else:
                print(Fore.RED + "No videos found.")
        
        if args.source_code:
            extract_source_code(url)
        
        if args.source_code_save:
            extract_source_code(url, output_directory="source_code", save_to_file=True)
        
        if args.scripts_with_src or args.scripts_without_src:
            scripts_with_src, scripts_without_src = extract_scripts(soup)
            if args.scripts_with_src:
                if scripts_with_src:
                    create_directory("scripts")
                    save_to_file(scripts_with_src, "scripts/scripts_with_src_found.txt")
                    print(Fore.GREEN + "Scripts with src attribute saved in 'scripts/scripts_with_src_found.txt'")
                else:
                    print(Fore.RED + "No scripts with src attribute found.")
            
            if args.scripts_without_src:
                if scripts_without_src:
                    create_directory("scripts")
                    save_to_file(scripts_without_src, "scripts/scripts_without_src_found.js")
                    print(Fore.GREEN + "Scripts without src attribute saved in 'scripts/scripts_without_src_found.js'")
                else:
                    print(Fore.RED + "No scripts without src attribute found.")

if __name__ == "__main__":
    main()
