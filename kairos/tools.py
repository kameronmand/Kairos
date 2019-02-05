# File: tools.py
import os
from datetime import datetime, timedelta
import time

from kairos import debug
from collections import OrderedDict
from configparser import RawConfigParser

log = debug.create_log()


def get_config(current_dir):
    config = RawConfigParser(allow_no_value=True, strict=False, empty_lines_in_values=False, dict_type=ConfigParserMultiValues, converters={"list": ConfigParserMultiValues.getlist})
    config_file = os.path.join(current_dir, "kairos.cfg")
    if os.path.exists(config_file):
        config.read(config_file)
        if config.getboolean('logging', 'clear_on_start_up'):
            debug.clear_log()
        log.setLevel(config.getint('logging', 'level'))
    else:
        log.error("File " + config_file + " does not exist")
        log.exception(FileNotFoundError)
        exit(0)
    return config


def chunks(collection, size):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(collection), size):
        yield collection[i:i + size]


class ConfigParserMultiValues(OrderedDict):

    def __setitem__(self, key, value):
        if key in self and isinstance(value, list):
            self[key].extend(value)
        else:
            super().__setitem__(key, value)

    @staticmethod
    def getlist(value):
        value = str(value).strip().replace('\r\n', '\n')
        value = value.replace('\r', '\n')
        result = str(value).split('\n')
        return result


class Switch:
    def __init__(self, value): self._val = value

    def __enter__(self): return self

    # Allows traceback to occur
    def __exit__(self, type, value, traceback): return False

    def __call__(self, *mconds): return self._val in mconds


def to_csv(data, delimeter=','):
    result = ''
    log.info(str(type(data)) + ': ' + str(data))
    if isinstance(data, dict):
        for _key in data:
            if result == '':
                result = to_csv(data[_key])
            else:
                result = delimeter + to_csv(data[_key], delimeter)
    elif isinstance(data, list):
        for i in range(len(data)):
            if result == '':
                result = to_csv(data[i])
            else:
                result = delimeter + to_csv(data[i], delimeter)
    else:
        result = data
    return result


def get_timezone():
    timestamp = time.time()
    date_utc = datetime.utcfromtimestamp(timestamp)
    date_local = datetime.fromtimestamp(timestamp)
    date_delta = max(date_utc, date_local) - min(date_utc, date_local)
    timezone = '{0:0{width}}'.format(int(date_delta.seconds / 60 / 60), width=2) + '00'
    if date_local > date_utc:
        timezone = '+' + timezone
    elif date_local < date_utc:
        timezone = '-' + timezone
    return timezone


def dt_parse(t):
    ret = datetime.strptime(t[0:16], '%Y-%m-%dT%H:%M')
    if t[17] == '+':
        ret -= timedelta(hours=int(t[18:20]), minutes=int(t[20:]))
    elif t[17] == '-':
        ret += timedelta(hours=int(t[18:20]), minutes=int(t[20:]))
    return ret
