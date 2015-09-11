# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings
from scrapy.pipelines.files import FilesPipeline
import time
import scrapy
import shlex
import os
import getpass
from subprocess import Popen


def call_timeout(cmd, timeout):
    start = time.time()
    p = Popen(cmd)
    while time.time() - start < timeout:
        if p.poll() is not None:
            return True
        time.sleep(0.1)
    p.kill()
    #  return False
    raise OSError('command timed out')


class GrabPipeline(object):
    def process_item(self, item, spider):
        return item


class NFSPipeline(FilesPipeline):

    def __init__(self, *args, **kwargs):
        super(NFSPipeline, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        self.ip = settings['NFS_SERVER']
        self.resource = settings['NFS_RESOURCE']
        self.store_dir = settings['FILES_STORE']
        self.port = settings['NFS_PORT']
        self.protocol = settings['NFS_PROTOCOL']

    def get_media_requests(self, item, info):
        self.check_nfs()

        for file_url in item['file_urls']:
            yield scrapy.Request(file_url)

    """
    We shall check(by steps):
        1. Whether this NFS server is online.
        2. Does this folder exists?
        2. Is this folder mounted?
        3. If NFS is not mounted, mount it to FILES_STORE in settings. """

    def check_nfs(self):
        command = shlex.split('showmount -d %s --no-headers' % self.ip)
        if call_timeout(command, 10):
            self.check_dir()
            return

    def check_if_mount(self):
        if not os.path.ismount(self.store_dir):
            return self.mount_nfs()
        else:
            return

    def check_dir(self):
        try:
            os.makedirs(self.store_dir)
        except OSError:
            if not os.path.isdir(self.store_dir):
                raise
        return self.check_if_mount()

    def mount_nfs(self):
        username = getpass.getuser()
        cmd = (
            'sudo mount -t nfs -o owner={username},proto={protocol},port={port}'
            ' {ip}:{resource} {store_dir}').format(**{
                'username': username,
                'port': self.port,
                'protocol': self.protocol,
                'ip': self.ip,
                'resource': self.resource,
                'store_dir': self.store_dir})
        if call_timeout(shlex.split(cmd), 10):
            return
