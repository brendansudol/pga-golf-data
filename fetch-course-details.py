import json
import os
import re
import requests

from glob import glob
from random import random
from time import sleep
from urllib.request import urlretrieve


BASE_HOLE_URL = 'http://i.pgatour.com/image/upload/c_fill,w_720,b_rgb:424141,b_rgb:424242'
COURSE_FILES = glob('data/tournaments/*/*/course.json')


def maybe_make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def run():
    course_files = glob('data/tournaments/*/*/course.json')

    for c_file in course_files:
        print('parsing {}...'.format(c_file))

        m = re.match(r'data/tournaments/(\d+)/(\d+)/', c_file)
        tid, yr = m.group(1), m.group(2)

        with open(c_file) as f:
            data = json.load(f)

        courses = data['courses']
        for course in courses:
            cid, cname = course['number'], course['name']
            print('{}...'.format(cname))

            course_dir = 'data/courses/{}/{}'.format(cid, yr)
            maybe_make_dir(course_dir)
            with open('{}/info.json'.format(course_dir), 'w') as f:
                json.dump(course, f, ensure_ascii=False)

            holes = [
                (num, '{}/holes_{}_r_{}_{}_overhead_full_{}.jpg'.format(
                    BASE_HOLE_URL, yr, tid, cid, num
                )) for num in range(1, 19)
            ]
            print('hole URLs sample: {}'.format(holes[:5]))

            # try first hole
            hole1_url = holes[0][1]
            res_code = requests.get(hole1_url, timeout=10).status_code

            if res_code != 200:
                print('could not find 1st hole image ({})'.format(res_code))
                continue

            hole_dir = '{}/holes'.format(course_dir)
            maybe_make_dir(hole_dir)

            for num, url in holes:
                try:
                    urlretrieve(url, '{}/{}.jpg'.format(hole_dir, num))
                except Exception as e:
                    print('error fetching {} ({})'.format(url, str(e)))

                if num % 6 == 0:
                    sleep(1 + random())


if '__main__' == __name__:
    run()
