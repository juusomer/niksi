import asyncio
import logging
import csv

import aiohttp
from tqdm import tqdm
from bs4 import BeautifulSoup


NIKSI_URL = 'http://www.pirkka.fi/niksit-ajax'
MAX_REQUESTS = 5
ITEMS_PER_PAGE = 9


async def fetch(url, session):
    async with session.get(url) as resp:
        return await resp.json()

async def fetch_with_semaphore(url, session, semaphore):
    async with semaphore:
        return await fetch(url, session)


def get_child(parent, child_tag, child_class):
    return parent.find(child_tag, {'class': child_class})

def get_child_content(parent, child_tag, child_class):
    child = get_child(parent, child_tag, child_class)
    return ''.join(child.contents).strip()

def parse_niksit(niksi_json):
    niksit = []
    soup = BeautifulSoup(niksi_json['html'], 'html.parser')

    for niksi in soup.find_all('div', {'class': 'lifehack-card-body'}):
        category = get_child_content(niksi, 'div', 'lifehack-card-category')
        contents = get_child_content(niksi, 'div', 'lifehack-card-text')
        title = get_child_content(niksi, 'h5', 'lifehack-card-title')
        id_field = get_child(niksi, 'span', 'lifehack-action-button')
        niksit.append({
            'category': category,
            'contents': contents,
            'title': title,
            'id': id_field['data-lifehack-id'],
        })

    return niksit


async def scrape_niksit():
    async with aiohttp.ClientSession() as session:
        niksi_json = await fetch(NIKSI_URL, session)
        pages = niksi_json['total'] // ITEMS_PER_PAGE

        semaphore = asyncio.Semaphore(MAX_REQUESTS)
        tasks = []
        for page in range(1, pages + 1):
            url = '{}?page={}'.format(NIKSI_URL, page)
            request = fetch_with_semaphore(url, session, semaphore)
            tasks.append(asyncio.ensure_future(request))

        with open('niksit.csv', 'w+') as f:
            fieldnames = fieldnames=('id', 'category', 'title', 'contents')
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                niksi_json = await task
                for niksi in parse_niksit(niksi_json):
                    writer.writerow(niksi)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_niksit())
