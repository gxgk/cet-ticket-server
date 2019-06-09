# -*- coding: utf-8 -*-
import os
import logging.config
import logging

DSN = os.environ.get('DSN')
DEBUG = os.environ.get('DEBUG', False)

application_settings = {
    'debug': DEBUG,
    'template_path': 'templates',
    'static_path': 'static'
}

# 开发时的日志配置，INFO 及以上级别的日志输出到 console。
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'handlers': ['console'],
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s [%(module)s|%(lineno)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': 'logs/default.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5
        }
    },
    'loggers': {
        'tornado': {
            'handlers': ['console', 'default'],
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('root')

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PWD = os.environ.get('REDIS_PWD', '')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_CHANNEL = os.environ.get('REDIS_CHANNEL', 0)

REDIS_URL = 'redis://:{}@{}:{}/{}'.format(REDIS_PWD, REDIS_HOST, REDIS_PORT, REDIS_CHANNEL)
