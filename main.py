#!/bin/python3

from bs4 import BeautifulSoup
import requests
import sys
import time
import os
import re

def validate_file_name(origi_name):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", origi_name)  # 替换为下划线
    return new_title

def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


def get_title(soup):
    metas = soup.head.find_all('meta')
    for meta in metas:
        if meta.get('property') == 'og:title':
            return meta.get('content')
    return 'default-' + str(time.time())


def get_image_links(soup: BeautifulSoup):
    items = soup.find_all('img', class_='rich_pages')
    return [i.get('data-src') for i in items]

def download_images(title, image_links):
    downloads_path = os.path.join('.', 'Downloads', validate_file_name(title))
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    
    index = 0
    for link in image_links:
        response = requests.get(link)
        with open(os.path.join(downloads_path, '%03d' % index), 'wb') as f:
            f.write(response.content)
        index = index + 1

def main(url):
    html = get_html(url)
    # with open('1.html', 'w') as f:
    #     f.write(html)
    soup = BeautifulSoup(html, 'lxml')
    title = get_title(soup)
    image_links = get_image_links(soup)
    download_images(title, image_links)
    return 0


if __name__ == '__main__':
    print('Comic Image Downloader V0.1')
    while True:
        link = input('Enter link: ')
        if link.lower() == 'bye':
            exit()
        main(link)