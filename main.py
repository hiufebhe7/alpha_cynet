import json
import os
import sys
import time

import requests
from mastodon import MastodonNetworkError

from src.utils import Pack, Upload, Download


def test_connect(instance):
    try:
        requests.get('https://' + instance, stream=True)
    except Exception as e:
        print(str(e))
        return
    finally:
        print('network is ready')


def generate_upload(path_file_login, path_upload):
    if not os.path.isfile(path_file_login):
        print('login file error~')
        return

    if not os.path.isdir(path_upload):
        print('upload path error~')
        return

    file_uploads = []
    for file in os.listdir(path_upload):
        file_uploads.append(file)

    file_login = open(path_file_login, 'rb')
    json_login = json.loads(file_login.read())
    file_login.close()

    json_task = {}
    json_task['type'] = 'upload'
    json_task['instance'] = json_login['instance']
    json_task['username'] = json_login['username']
    json_task['password'] = json_login['password']
    json_task['path'] = path_upload

    json_task['jobs'] = []

    for p in file_uploads:
        json_task['jobs'].append({
            'md5': '',
            'name': p,
            'status': 0
        })

    str_out = json.dumps(json_task)
    file_name = 'task.u.' + str(int(time.time())) + '.json'
    file_out = open(file_name, 'wb')
    file_out.write(str_out.encode())
    file_out.close()

    print('generate upload task: ' + file_name)
    return file_name


def upload(path_file_task):
    if not os.path.isfile(path_file_task):
        print('task load error')
        return

    print('start ' + path_file_task)
    upload = Upload()

    f = open(path_file_task, 'rb')
    data = f.read()
    f.close()

    json_task = json.loads(data)

    f = open(path_file_task, 'ab')

    jobs = json_task['jobs']

    while True:
        t = None
        try:
            t = upload.task(json_task)
        except (ConnectionResetError, MastodonNetworkError) as e:
            print(str(e))
            f.close()
            return
        if not t:
            break
        f.truncate(0)
        f.write(json.dumps(t).encode())

    pack = Pack()
    url = pack.encode_url('cynet:?p=https:i=' + json_task['instance'] + ':', jobs)
    print('encode task to url:')
    print(url)

    f.close()


def generate_download(url, path_download):
    if os.path.isdir(path_download):
        json_task = {}
        json_task['type'] = 'download'
        json_task['path'] = path_download

        pack = Pack()
        jobs = pack.decode_url(url)
        json_task['jobs'] = jobs

        for job in jobs:
            job['status'] = 0

        str_out = json.dumps(json_task)
        path_file_task = 'task.d.' + str(int(time.time())) + '.json'
        file_in = open(path_file_task, 'wb')
        file_in.write(str_out.encode())
        file_in.close()
        print('generate download task: ' + path_file_task)


def download(path_file_task):
    print('start ' + path_file_task)

    if os.path.isfile(path_file_task):

        file_in = open(path_file_task, 'rb')
        str_task = file_in.read()
        file_in.close()

        download = Download()
        json_task = json.loads(str_task)
        f = open(path_file_task, 'ab')

        while True:
            t = None
            try:
                t = download.task(json_task)
            except (ConnectionResetError, MastodonNetworkError) as e:
                print(str(e))
                f.close()
                return
            if not t:
                break
            f.truncate(0)
            f.write(json.dumps(t).encode())

        # jobs = json_task['jobs']
        print('\r***download end***',
              end='', flush=True)
        f.close()


def cli(argv):
    type_task = argv[1]

    # len_params = len(argv)
    # print('debug', argv)

    if type_task == 't':
        test_connect(argv[2])

    elif type_task == 'gu':
        generate_upload(argv[2], argv[3])

    elif type_task == 'gd':
        generate_download(argv[2], argv[3])

    elif type_task == 'u':
        upload(argv[2])

    elif type_task == 'd':
        download(argv[2])

    else:
        print('params error')


if __name__ == '__main__':
    cli(sys.argv)
