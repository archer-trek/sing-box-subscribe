import importlib
import os
import threading


__PARSERS = {}
__LOCK = threading.Lock()


def __init_parsers():
    parsers = {}
    for path, dirs, files in os.walk('parsers'):
        for file in files:
            f = os.path.splitext(file)
            if f[1] == '.py' and f[0] != '__init__':
                parsers[f[0]] = importlib.import_module('parsers.' + f[0]).parse
    return parsers


def get_parser(proto):
    global __PARSERS

    if not __PARSERS:
        with __LOCK:
            if not __PARSERS:
                __PARSERS = __init_parsers()

    return __PARSERS.get(proto)
