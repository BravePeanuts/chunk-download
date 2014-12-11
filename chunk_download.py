#!/usr/bin/python
# _*_ coding: utf-8 _*_

import threading
import requests
import os

url = 'http://dl.fonts.cache.wps.cn/fonts/free/2014-9-4/5408178a82283.ttf.zip'
dir_path = '%s/%s' % (os.path.dirname(__file__), 'font.ttf.zip')
chunk_bytes = 65536         # 分块大小
lock = threading.RLock()    # 初始化lock


def get_range():
    """获取文件的大小

    return:
        如果文件存在返回字节，否则返回None
    """
    ret = requests.head(url)
    if ret.headers.get('accept-ranges'):
        return int(ret.headers.get('content-length'))
    else:
        return None


def write_file(start, buf, f):
    f.seek(start)
    f.write(buf)


def chunk_download(n, length, f):

    start = chunk_bytes * n
    end = chunk_bytes * (n + 1) - 1

    if end >= length:
        end = length - 1

    headers = dict()
    headers['Range'] = 'bytes=%s-%s' % (start, end)
    print '分块 thread:%s Range: %s 下载开始' % (n, headers['Range'])
    ret = requests.get(url, headers=headers)

    with lock:
        write_file(start, ret.content, f)


def download(f):
    print '整文件开始下载'
    ret = requests.get(url)
    f.write(ret.content)


class DownloadThread(threading.Thread):
    def __init__(self, tid, length, f):
        self.tid = tid
        self.length = length
        self.f = f
        super(DownloadThread, self).__init__()

    def run(self):
        chunk_download(self.tid, self.length, self.f)


if __name__ == '__main__':

    f = open(dir_path, 'wb')
    plist = []
    content_length = get_range()
    if not content_length:
        # download full file
        download(f)

    else:
        # download file trunk
        block = content_length / chunk_bytes + 1

        for i in range(0, block):
            t = DownloadThread(i, content_length, f)
            plist.append(t)

    for t in plist:
        t.start()

    for t in plist:
        t.join()

    f.close()
    print '文件下载完成'