import base64
import random
import string
from time import sleep, time
import requests
import logging


def genName(length=8):
    name = ''
    for i in range(length):
        name += random.choice(string.ascii_letters+string.digits)
    return name


def b64Decode(str):
    str = str.strip()
    str += (len(str) % 4)*'='
    return base64.urlsafe_b64decode(str)


def http_get_content(url, user_agent=None, retry_times=5) -> str:
    default_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15'
    headers = {
        'User-Agent': user_agent if user_agent else default_ua
    }

    for i in range(retry_times):
        content = __http_get_content(url, headers)
        if content is not None:
            return content
        else:
            sleep(0.3)
            logging.warning('retry http get %s (%s/%s)', url, i+1, retry_times)

    return None


def __http_get_content(url, headers):
    try:
        start_time = time()
        response = requests.get(url, headers=headers, timeout=180)
        cost_time = int((time() - start_time) * 1000)
        if response.status_code == 200:
            logging.info('http get %s cost time: %s ms', url, cost_time)
            return response.text
        else:
            logging.error('http get %s failed, cost time: %s ms, code %s, %s',
                          url, cost_time, response.status_code, response.text)
            return None
    except Exception as e:
        logging.error('http get %s failed, %s', url, e)
        return None
