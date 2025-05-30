import os
from uuid6 import uuid7
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

def create_image_url(img):
    file_name = f"{uuid7()}{os.path.splitext(img.name)[1]}"
    path = f'ad_images/{file_name}'

    default_storage.save(path, ContentFile(img.read()))

    return os.path.join(settings.MEDIA_URL, path)