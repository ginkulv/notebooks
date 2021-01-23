import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs

client = MongoClient()
db = client.opinions_db
collection = db.opinions

for num_page in range(8, 14):
    url = f'https://www.citilink.ru/catalog/mobile/smartfony/?p={num_page}'
    r = requests.get(url)
    data = bs(r.content)

    links = data.findAll('a', {'class': 'Link js--Link Link_type_default'})
    links.pop(0)
    links = [link for link in links[::2]]
    links = list(set(links))

    urls = [link.get('href') for link in links]

    posturls = []
    for url in urls:
        spliturl = url.split('/')
        spliturl[-2] = "getall-opinion"
        posturls.append("/".join(spliturl))

    for url in posturls:
        try:
            raw = requests.post(url, headers={'X-Requested-With': 'XMLHttpRequest'}).json()
            html = bs(raw.get('html'))
            opinions = html.findAll('div', {'class': 'Opinion'})
            for opinion in opinions:
                rate = opinion.find('span', {'class': 'Opinion__number'}).text.strip()
                messages = opinion.findAll('p', {'class': 'Opinion__text'})
                titles = opinion.findAll('div', {'class': 'Opinion__title'})
                advantages, disadvantages, comment = '', '', ''
                for message, title in zip(messages, titles):
                    if 'Достоинства' in title.text:
                        advantages = message.text.strip().replace('\n', ' ')
                    elif 'Недостатки' in title.text:
                        disadvantages = message.text.strip().replace('\n', ' ')
                    else:
                        comment = message.text.strip().replace('\n', ' ')
                opinion = {
                        "rate": rate,
                        "advantages": advantages,
                        "disadvantages": disadvantages,
                        "comment": comment
                        }
                collection.insert_one(opinion)
        except:
            continue

