import binascii
import gzip
import hashlib
import json
import os

import requests
from mastodon import Mastodon, MastodonNetworkError, MastodonIllegalArgumentError

from src.config import config


class Pack:

    def __init__(self) -> None:
        super().__init__()
        f = open('./cache/null.mp4', 'rb')
        self.data_null = f.read()
        f.close()

    def pack(self, data_source):
        # file_upload = open(path_file_source, 'rb')
        # data_upload = file_upload.read()
        # file_upload.close()

        # file_null = open(path_file_null, 'rb')
        # data_null = file_null.read()
        # file_null.close()

        return self.data_null + data_source

    def unpack(self, data_pack):
        # file_pack = open(path_file_pack, 'rb')
        # data_pack = file_pack.read()
        # file_pack.close()

        # file_null = open(path_file_null, 'rb')
        # data_null = file_null.read()
        # file_null.close()

        return data_pack[len(self.data_null):]

    def encode_url(self, header, json_jobs):
        # links_b = b"\x1f\x8b\x08\x00V\xa37^\x02\xff\xad\xce\xc1\x8e\x83 \x14@\xd1_1\xac\x1bx\x0f\x10x\xfd\x95v2A\x84\x96D\xd4T\xcc$m\xfa\xef\xe3\xac\xdc;\xdd\xdd\xdd=\x97\x17[\x1f\x03;7\xec^\xeb\xbc\x9c\x85\xc8\xe5\xc6g\xff3M|\x8cU\x94\xd8g\xff\xedk\xf5\xe1^\xe2X\x17\x91\xf2\x10\x17\x01R\x0bD+\xc0Y1=\xf2-\x8f~\x10\xa1G\x03\x16\xda\xe0R\xaber\xbc\xcc\x9a\x9d\x1a6\xfa\x12\xff\x16\xd7\xb5UQ_WJD[\xa3q[\x9b`\x1ak\xb6\x80\xe8\xf83\xcf\x1c\x00\xd9\xfb\xd4\xfc\x1bF;\xcc\x04J-\x92\xd6\x1a\x9c\x8e\xd6\x1e\x85\xc9O\xc0\x08v\x18t\x0et'\xa9S19+\xf1(L}\x04\x86;,\x05\xa7\x00\x95\xed,\xf4\n\x89\x8e\xc24{\x7f\xfd\x02\xdc2\xc7\xf1d\x02\x00\x00"
        str_jobs = json.dumps(json_jobs)
        gzip_jobs = gzip.compress(str_jobs.encode())
        list_jobs = list(gzip_jobs)
        list_hexs = []
        for i in list_jobs:
            n = hex(i)
            n = str(n)
            n = n.replace('0x', '')
            if i < 16:
                n = '0' + n
            list_hexs.append(n)
        links_b = ''.join(list_hexs)
        url = header + 'u=' + links_b
        return url

    def decode_url(self, url):

        link_header = url.split(':?')[0]
        link_body = url.split(':?')[1]
        link_body = link_body.split(':')
        protocol = link_body[0].split('=')[1]
        instance = link_body[1].split('=')[1]
        gzip_jobs = link_body[2].split('=')[1]

        lurls = list(gzip_jobs)
        lurls.reverse()
        gzip_jobs = []
        while len(lurls) > 0:
            fstr = ''
            if len(lurls) > 1:
                fstr = lurls.pop()
            else:
                fstr = '0'
            lstr = lurls.pop()
            i_hex = fstr + lstr
            gzip_jobs.append(binascii.unhexlify(i_hex))
        gzip_jobs = b''.join(gzip_jobs)

        jobs = gzip.decompress(gzip_jobs)
        jobs = json.loads(jobs)
        return jobs


class Upload:

    def __init__(self) -> None:
        super().__init__()
        self.api = None
        self.pack = None

    def __connect(self, instance, username, password):

        url = 'https://' + instance

        try:
            Mastodon.create_app(
                'pytooterapp',
                api_base_url=url,
                to_file='./cache/pytooter_clientcred.secret'
            )

            mastodon = Mastodon(
                client_id='./cache/pytooter_clientcred.secret',
                api_base_url=url
            )

            mastodon.log_in(
                username,
                password,
                to_file='./cache/pytooter_usercred.secret'
            )
            return mastodon
        except (MastodonNetworkError, MastodonIllegalArgumentError) as e:
            return None

    def task(self, json_task):

        if not self.api:

            if not os.path.isdir(json_task['path']):
                return None

            self.api = self.__connect(
                instance=json_task['instance'],
                username=json_task['username'],
                password=json_task['password']
            )

            if self.api == None:
                print('internet connect error')
                exit()

            self.pack = Pack()

        jobs = json_task['jobs']

        for job in jobs:

            path_file_upload = os.path.join(json_task['path'], job['name'])

            if job['status'] == 1:
                # print('上传完成:', job['url'], job['name'])
                continue
            else:
                print('start upload:', path_file_upload)

            f = open(path_file_upload, 'rb')
            data_source = f.read()
            f.close()

            pack_data = self.pack.pack(data_source)
            f = open(config.path_file_tmp, 'wb')
            f.write(pack_data)
            f.close()

            obj = hashlib.md5()
            obj.update(data_source)
            str_md5 = obj.hexdigest()

            response = self.api.media_post(config.path_file_tmp)
            job['md5'] = str_md5
            job['url'] = response['url']
            job['status'] = 1

            print('upload succuse:', job['url'], job['name'])
            return json_task

        return None


class Download:

    def task(self, json_task):

        i_donload = len(json_task['jobs'])
        i_donload_complete = 0
        for job in json_task['jobs']:

            if job['status'] == 1:
                i_donload_complete += 1
                continue

            response = requests.get(job['url'], stream=True)
            count = 0
            all_cout = int(response.headers['Content-Length'])
            datas = []
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    count += len(chunk)
                    # print(len(chunk))
                    datas.append(chunk)
                    print('\rdownload file:',
                          job['name'],
                          str(i_donload_complete) + '/' + str(i_donload),
                          str(int(count / all_cout * 1000)/10) + '%',
                          end='', flush=True)

            file_out = open(os.path.join(json_task['path'], job['name']), 'wb')
            data = b''.join(datas)
            pack = Pack()
            data_unpack = pack.unpack(data)

            obj = hashlib.md5()
            obj.update(data_unpack)
            str_md5 = obj.hexdigest()
            if str_md5 == job['md5']:
                file_out.write(data_unpack)
            else:
                print('download file md5 error')
                json_task = None
            file_out.close()

            job['status'] = 1
            return json_task
        return None
