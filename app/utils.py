import random
import string
import base64
import pickle
from app import redis


def generate_random_str(N):
    """生成随机字符串"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N))


