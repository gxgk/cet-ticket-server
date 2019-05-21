import os
import pickle

from app import redis


def del_file(file_name):
    ''' 删除文件 '''
    if os.path.exists(file_name):
        os.remove(file_name)


def set_cache(key, values):
    redis.set(key, pickle.dumps(values))


def get_cache(key):
    cache_data = redis.get(key)
    if cache_data:
        cache_data = pickle.loads(cache_data)

    return cache_data
