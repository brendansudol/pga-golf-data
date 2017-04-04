import json
import os
import requests

from random import random
from time import sleep


BASE_URL = 'http://www.pgatour.com/data/r'
BASE_DATA_DIR = 'data/tournaments'
YEARS = ['2015', '2016']
COURSE_IDS = [
    '002', '003', '004', '005', '006', '007', '009', '010', '011',
    '012', '013', '014', '016', '018', '019', '020', '021', '023',
    '025', '026', '027', '028', '030', '032', '033', '034', '041',
    '047', '054', '058', '060', '100', '457', '464', '471', '472',
    '473', '475', '476', '480', '483', '489', '490', '493', '494',
    '505', '518',
]


def save(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def maybe_make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_json(url):
    print('fetching {}...'.format(url))
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return

    return json.loads(response.content.decode('utf-8'))


def fetch_and_save(url, dir_path, fname):
    try:
        data = get_json(url)
    except Exception as e:
        print('error fetching {} ({})'.format(url, str(e)))
        return

    if not data:
        return

    maybe_make_dir(dir_path)
    save(data, '{}/{}'.format(dir_path, fname))

    return data


def run():
    for cid in COURSE_IDS:
        course = fetch_and_save(
            '{}/{}/course.json'.format(BASE_URL, cid),
            '{}/{}'.format(BASE_DATA_DIR, cid),
            'course.json',
        )

        if not course:
            print('cannot find course {}'.format(cid))
            continue

        for yr in YEARS:
            summary = fetch_and_save(
                '{}/{}/{}/leaderboard-v2.json'.format(BASE_URL, cid, yr),
                '{}/{}/{}'.format(BASE_DATA_DIR, cid, yr),
                'summary.json',
            )

            if not summary:
                print('no tourney summary for {}'.format(yr))
                continue

            sleep(1 + random())
            players = [p['player_id'] for p in summary['leaderboard']['players']]
            print('{} players found'.format(len(players)))

            for i, pid, in enumerate(players):
                fetch_and_save(
                    '{}/{}/{}/scorecards/{}.json'.format(BASE_URL, cid, yr, pid),
                    '{}/{}/{}/scorecards'.format(BASE_DATA_DIR, cid, yr),
                    '{}.json'.format(pid),
                )

                if i and i % 5 == 0:
                    print('done with {} players'.format(i))
                    sleep(1 + random())


if '__main__' == __name__:
    run()
