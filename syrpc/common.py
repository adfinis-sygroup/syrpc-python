# -*- coding: UTF-8 -*-

"""Common classes / functions"""

# System imports
import logging
import siphashc
import sys

# Project imports
import symonitoring_rpc.constants as const

_setup_done = False


def _setup_logger(level, stdout=False, stderr=False):  # pragma: no cover
    """Sets up a default logger"""
    global _setup_done  # pylint: disable=global-statement
    if _setup_done:
        return
    _root = logging.getLogger()
    _lg = _root.getChild(const.General.APP_NAME)
    if stdout:
        _stdout_handler = logging.StreamHandler(sys.stdout)
        _root.addHandler(_stdout_handler)
    if stderr:
        _stderr_handler = logging.StreamHandler(sys.stderr)
        _root.addHandler(_stderr_handler)
    _root.setLevel(level)
    _setup_done = True
    return _lg


def get_body_encoding(body, default_encoding='utf-8'):
    """Tries to get encoding of 'body', splitted by \0"""
    body = body.split('\0', 1)
    if len(body) <= 1:
        encoding = default_encoding
        body = body[0]
    else:
        encoding = body[0]
        body = body[1]
    return (body, encoding)


def get_hash(string, queue_count=const.AMQ.NUM_QUEUES):
    """Generates a hash for given string"""
    # Only use the last 31 bits of the 64-bit hash because of serious
    # PHP-retardedness
    hash32 = siphashc.siphash(const.AMQ.HASH, string) & 0x7FFFFFFF  # pylint: disable=no-member
    return hash32 % queue_count


def consts_to_dict(object_):  # pragma: no cover
    """Converts a constants object to a dictionary"""
    new = {}
    for const_ in dir(object_):
        if not const_.startswith("_"):
            new[getattr(object_, const_)] = const_
    return new


lg = _setup_logger(logging.WARN)
