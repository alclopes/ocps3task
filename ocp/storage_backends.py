from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    #location = settings.STATICFILES_LOCATION
    location = 'static'
    default_acl = 'public-read'


class MediaStorage(S3Boto3Storage):
    #location = settings.MEDIAFILES_LOCATION
    location = 'media'
    file_overwrite = False
    default_acl = 'public-read'
