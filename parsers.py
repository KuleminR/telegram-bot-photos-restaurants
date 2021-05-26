import requests
import json

from bs4 import BeautifulSoup

# google search
google_search_url = 'https://www.googleapis.com/customsearch/v1'
search_id = 'your app id'
api_key = 'your api key'
search_term = 'your search term'

# Fastfood events
mcdonalds_events = 'https://mcdonalds.ru/events'


def get_photo_google(name, sum_res_parameter_name, file_to_save_links):
    with open('db.txt', 'r') as f:
        data = json.load(f)
        sum_results = data[sum_res_parameter_name]

    try:
        r = requests.get(google_search_url, {'key': api_key,
                                             'cx': search_id,
                                             'q': name,
                                             'ImgSize': 'large',
                                             'searchType': 'image',
                                             'num': 10,
                                             'start': sum_results + 1,
                                             })
    except(Exception):
        print('Something went wrong')

    response_dict = r.json()
    if 'error' in response_dict.keys():
        print(response_dict['error']['message'])
        data['resource_available'] = False
        with open ('db.txt', 'w') as f:
            json.dump(data, f)
    else:
        data[sum_res_parameter_name] = sum_results + 10
        data['resource_available'] = True
        with open ('db.txt', 'w') as f:
            json.dump(data, f)

        photo_links_list = []
        try:
            for item in response_dict['items']:
                photo_links_list.append(item['link'] + '\n')
        except(KeyError):
            data[sum_res_parameter_name] = sum_results + 2
            with open('db.txt', 'w') as f:
                json.dump(data, f)

        with open(file_to_save_links, 'a') as f:
            f.writelines(photo_links_list)


def get_new_photo_base(n):
    for i in range(n):
        get_photo_google(photo_search_tesrm, 'photo_sum_results', 'photo_links.txt')


def get_mcdonalds_events():
    img_mockup = 'https://cdn.mos.cms.futurecdn.net/xDGQ9dbLmMpeEqhiWayMRB-1200-80.jpg'
    r = requests.get(mcdonalds_events)
    soup = BeautifulSoup(r.text, 'lxml')
    a_links = soup.find_all(class_='event__image')
    events_list = []

    for link in a_links:
        href = link['href']
        event_link = ''
        if not href.startswith('https://'):
            event_link += 'https://mcdonalds.ru'
            if 'events' not in href:
                event_link += '/events'

        event_link += href

        r = requests.get(event_link)
        soup = BeautifulSoup(r.text, 'lxml')
        img = soup.find(class_='page-promo__img')
        if img:
         img_link = 'https://mcdonalds.ru/' + img.img['src']
        else:
         img_link = img_mockup

        events_list.append([event_link, img_link])
    return events_list