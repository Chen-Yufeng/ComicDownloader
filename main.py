#!/bin/python3

from bs4 import BeautifulSoup
import requests
import sys
import time
import os
import re
import img2pdf


def validate_file_name(origi_name):
    rstr = r"[\/\\\:\*\?\"\<\>\|\.]"  # '/ \ : * ? " < > |'
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

    index = 1
    for link in image_links:
        response = requests.get(link)
        if response.status_code != 200:
            retry = 0
            while True:
                retry = retry + 1
                print('Retry-%d: Image %03d' % (retry, index))
                response.close()
                response = requests.get(link)
                if (response.status_code == 200):
                    break
        with open(os.path.join(downloads_path, '%03d.jpg' % index), 'wb') as f:
            f.write(response.content)
        response.close()
        index = index + 1
    
    return downloads_path

def generate_pdf(title, path):
    pdf_path = os.path.join(path, validate_file_name(title) + '.pdf')
    with open(pdf_path, 'wb') as f:
        imgs = []
        for fname in os.listdir(path):
            if not fname.endswith('.jpg'):
                continue
            jpg_path = os.path.join(path, fname)
            if os.path.isdir(jpg_path):
                continue
            imgs.append(jpg_path)
        imgs.sort()
        f.write(img2pdf.convert(imgs))

def main(url):
    html = get_html(url)
    # with open('1.html', 'w') as f:
    #     f.write(html)
    soup = BeautifulSoup(html, 'lxml')
    title = get_title(soup)
    image_links = get_image_links(soup)
    downloads_path = download_images(title, image_links)
    generate_pdf(title, downloads_path)
    
    return 0


if __name__ == '__main__':
    print('Comic Image Downloader V0.1.2')
    while True:
        link = input('Enter link: ')
        if link.lower() == 'bye':
            exit()
        main(link)