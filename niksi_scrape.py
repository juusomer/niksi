import asyncio
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


async def get_number_of_pages(session):
    niksi_json = await fetch(NIKSI_URL, session)
    return niksi_json['total'] // ITEMS_PER_PAGE

async def fetch_page(page, session, semaphore):
    url = '{}?page={}'.format(NIKSI_URL, page)
    response = await fetch_with_semaphore(url, session, semaphore)
    return parse_niksit(response)

async def scrape_niksit():
    async with aiohttp.ClientSession() as session:
        pages = await get_number_of_pages(session)
        semaphore = asyncio.Semaphore(MAX_REQUESTS)
        requests = [
            fetch_page(page, session, semaphore)
            for page in range(1, pages + 1)
        ]
        with open('niksit.csv', 'w+') as f:
            fieldnames = fieldnames=('id', 'category', 'title', 'contents')
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            total = len(requests)
            for request in tqdm(asyncio.as_completed(requests), total=total):
                for niksi in await request:
                    writer.writerow(niksi)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_niksit())
