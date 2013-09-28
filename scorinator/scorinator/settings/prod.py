from .base import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

DATABASES = {'default': dj_database_url.config()}

LOGGING['root'] = {
            'level': 'WARNING',
            'handlers': ['opbeat']}
LOGGING['loggers']['opbeat'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False}
LOGGING['loggers']['opbeat.errors'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False}

LOGGING['handlers']['log_file']['filename'] = ''

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']