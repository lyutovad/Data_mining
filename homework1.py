import time
import json
import re
import requests


URL = 'https://5ka.ru/api/v2/special_offers/'
HEADERS = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
}

CAT_URL = 'https://5ka.ru/api/v2/categories/'


def x5ka(url, params):
    '''Получаем список продуктов по акции'''
    result = []
    while url:
        response = requests.get(url, headers=HEADERS, params=params) if params else requests.get(url, headers=HEADERS)
        params = None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(2)

    return result


def parent_group_name(data):
    '''Добавляем название родительской группы для каждого продукта'''
    for item in data:
        prod_id = str(item.get('id'))
        url = URL + prod_id
        response = requests.get(url, headers=HEADERS)
        data_prod = response.json()
        item['parent_group_name'] = data_prod['product']['group']['parent_group_name']

    return data


def list_of_groups(url):
    '''Список категорий с названиями групп'''
    response = requests.get(url, headers=HEADERS)
    categories = response.json()
    return categories


def write_files(products, categories):
    '''Смотрим имя каждой группы, записываем файл для группы, помещаем соответсвующие продукты'''
    for group in categories:
        name = group.get('parent_group_name')
        if re.findall('\*\\n\*', name):
            name = re.findall(r'\"(.+)\*', name)[0]
        with open(f'{name}.json', 'w') as file:
            for item in products:
                if item.get('parent_group_name') == name:
                    file.write(json.dumps(item))
    print('Файлы созданы')


if __name__ == '__main__':
    DATA = x5ka(URL, {'records_per_page': 100})
    EXTENDED_DATA = parent_group_name(DATA)
    CATEGORIES = list_of_groups(CAT_URL)
    write_files(EXTENDED_DATA, CATEGORIES)
