import json
import os
import requests

from random import random
from time import sleep

from slugify import slugify


base_url = 'http://www.pgatour.com/data/r'
years = ['2015', '2016']
course_ids = [
    '003', '007', '010', '012', '014', '018', '020', '023', '026',
    '028', '032', '034', '047', '060', '457', '471', '473', '476',
    '483', '490', '494', '518', '006', '009', '011', '013', '016',
    '019', '021', '025', '027', '030', '033', '041', '054', '100',
    '464', '472', '475', '480', '489', '493', '505'
]


def get_data(url):
    print('fetching {}...'.format(url))
    response = requests.get(url, timeout=5)

    if response.status_code != 200:
        return

    return json.loads(response.content.decode('utf-8'))


def maybe_make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


for course_id in course_ids:
    url = '{}/{}/course.json'.format(base_url, course_id)
    data = get_data(url)

    if not data:
        print('cannot find course {}'.format(course_id))
        continue

    course_name = data['courses'][0]['name']
    course_slug = slugify(course_name)

    course_dir = 'data/{}'.format(course_slug)
    maybe_make_dir(course_dir)
    save(data, '{}/course.json'.format(course_dir))

    for year in years:
        url = '{}/{}/{}/leaderboard-v2.json'.format(base_url, course_id, year)
        data = get_data(url)

        if not data:
            print('no data for {}'.format(year))
            continue

        year_dir = '{}/{}'.format(course_dir, year)
        maybe_make_dir(year_dir)
        save(data, '{}/leaderboard.json'.format(year_dir))

    sleep(1 + random())
