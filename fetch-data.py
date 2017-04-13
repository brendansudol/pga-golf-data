import json
import os
import requests

from random import random
from time import sleep
from urllib.request import urlretrieve


BASE_URL = 'http://www.pgatour.com/data/r'
BASE_HOLE_URL = 'http://i.pgatour.com/image/upload/c_fill,w_1000,b_rgb:222'
BASE_DATA_DIR = 'data/tournaments'
YEARS = ['2015', '2016']
TOURNEY_IDS = [
    '002', '003', '004', '005', '006', '007', '009', '010', '011',
    '012', '013', '014', '016', '018', '019', '020', '021', '023',
    '025', '026', '027', '028', '030', '032', '033', '034', '041',
    '047', '054', '058', '060', '100', '457', '464', '470', '471',
    '472', '473', '474', '475', '476', '478', '480', '483', '489',
    '490', '493', '494', '500', '505', '518', '519',
]


def hole_url(yr, tid, cid, num, view='full'):
    return '{}/holes_{}_r_{}_{}_overhead_{}_{}.jpg'.format(
        BASE_HOLE_URL, yr, tid, cid, view, num
    )


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
    for tid in TOURNEY_IDS:
        for yr in YEARS:
            data_url = '{}/{}/{}'.format(BASE_URL, tid, yr)
            data_dir = '{}/{}/{}'.format(BASE_DATA_DIR, tid, yr)

            # fetch course summary info

            course_dir = '{}/course'.format(data_dir)
            course_data = fetch_and_save(
                '{}/course.json'.format(data_url),
                course_dir,
                'overview.json',
            )

            if not course_data:
                print('cannot find course for {}'.format(tid))
                continue

            # fetch course details & imgs

            for course in course_data['courses']:
                print('{}...'.format(course['name']))
                cid = course['number']
                cid_dir = '{}/{}'.format(course_dir, cid)

                maybe_make_dir(cid_dir)
                save(course, '{}/info.json'.format(cid_dir))

                holes = [
                    {
                        'num': num,
                        'full': hole_url(yr, tid, cid, num, 'full'),
                        'green': hole_url(yr, tid, cid, num, 'green'),
                    } for num in range(1, 19)
                ]
                print('sample of hole URLs: {}'.format(holes[:5]))

                # try first hole
                hole1 = holes[0]['full']
                result = requests.get(hole1, timeout=10).status_code
                if result != 200:
                    print('course {}: no 1st hole img ({})'.format(cid, result))
                    continue

                hole_dir = '{}/holes'.format(cid_dir)
                maybe_make_dir(hole_dir)

                for hole in holes:
                    num = hole['num']
                    path_start = '{}/{}'.format(hole_dir, '{0:02d}'.format(num))
                    try:
                        urlretrieve(hole['full'], '{}_{}.jpg'.format(path_start, 'full'))
                        urlretrieve(hole['green'], '{}_{}.jpg'.format(path_start, 'green'))
                    except Exception as e:
                        print('error with {} ({})'.format(hole, str(e)))
                    if num % 6 == 0:
                        sleep(1 + random())

            # fetch tourney (scoring) summary

            summary = fetch_and_save(
                '{}/leaderboard-v2.json'.format(data_url),
                data_dir,
                'summary.json',
            )

            if not summary:
                print('no tourney summary for {}'.format(yr))
                continue

            # fetch player tourney scorecards

            players = [p['player_id'] for p in summary['leaderboard']['players']]
            print('{} players found'.format(len(players)))

            for i, pid, in enumerate(players):
                fetch_and_save(
                    '{}/scorecards/{}.json'.format(data_url, pid),
                    '{}/scorecards'.format(data_dir),
                    '{}.json'.format(pid),
                )

                if i and i % 5 == 0:
                    print('done with {} players'.format(i))
                    sleep(1 + random())


if '__main__' == __name__:
    run()
