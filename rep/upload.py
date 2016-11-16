"""
Handles file upload
"""

from rep import photos, app
import os
import requests


class Upload(object):

    @staticmethod
    def list_dir_no_hidden(path):
        for f in os.listdir(path):
            if not f.startswith('.'):
                yield f

    @staticmethod
    def get_all_urls():
        urls = []
        img_names = Upload.list_dir_no_hidden(app.config['UPLOADED_PHOTOS_DEST'])

        for img in img_names:
            urls.append(Upload.get_url(img))
        return urls

    @staticmethod
    def exists(img_name):
        url = photos.url(img_name)
        r = requests.get(url)
        return r.status_code == 200

    @staticmethod
    def get_url(img_name):
        return photos.url(img_name)

    @staticmethod
    def save(img_name, img):
        if Upload.exists(img_name):
            return Upload.get_url(img_name)

        url = photos.save(storage=img, name=img_name)
        return url
