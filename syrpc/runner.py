# -*- coding: UTF-8 -*-
# pylint: disable=super-init-not-called

"""Test module with example implementations"""

# System import
import logging
import os
import sys
import time
# Project imports
import syrpc.common as cmn
import syrpc.server as srv
import syrpc.client as cl


def setup_logger():
    """Sets up loggers"""
    rpc_logger = logging.getLogger('syrpc')
    if 'SYRPC_DEBUG' in os.environ:
        rpc_logger.setLevel(logging.DEBUG)
    else:
        rpc_logger.setLevel(logging.CRITICAL)
    rpc_log_handler = logging.StreamHandler(sys.stdout)
    rpc_logger.addHandler(rpc_log_handler)


def get_settings():
    """Returns settings to be used for clients and servers"""
    return {
        'app_name':        'syrpc',
        'amq_virtualhost': '/',
        'amq_host':        'localhost',
        'amq_user':        'guest',
        'amq_password':    'guest',
    }


def server(sleep=False, timeout=10, runner=False):
    """syrpc Server main routine"""
    settings = get_settings()
    setup_logger()
    rpc_server = srv.Server(settings)
    if runner:
        while True:
            run_server(rpc_server=rpc_server, timeout=timeout, sleep=sleep)
    else:
        run_server(rpc_server=rpc_server, timeout=timeout, sleep=sleep)


def server_runner():
    """syrpc Server runner routine"""
    server(runner=True, timeout=None)


def run_server(rpc_server, timeout, sleep):
    """Runs server"""
    (type_, result_id, data) = rpc_server.get_request(timeout=timeout)
    cmn.lg.info("Server received request: %s" % (result_id))
    if sleep:
        time.sleep(0.5)
    if type_ == 'ping':
        data = {
            'data':  {'is_running': 'true'},
        }
        rpc_server.put_result(
            result_id=result_id, data=data
        )
        cmn.lg.debug("Server put result: {0}".format(result_id))
    else:
        cmn.lg.debug("Server got no request within timeout")


def client(sleep=False, timeout=10, runner=False, num_requests=1):
    """syrpc Client main routine"""
    settings = get_settings()
    setup_logger()
    rpc_client = cl.Client(settings)
    if runner:
        while True:
            run_client(rpc_client, timeout, sleep, num_requests)
    else:
        run_client(rpc_client, timeout, sleep, num_requests)


def two_clients(timeout=10):
    """Runs two independent clients."""
    settings = get_settings()
    setup_logger()
    rpc_client_1 = cl.Client(settings)
    type_ = 'ping'
    data = [{'foo': 'bar'}, {'baz': 9001}]
    result_id = rpc_client_1.put_request(type_=type_, data=data)
    cmn.lg.debug("Client 1 put request for result {0}".format(
        result_id
    ))
    time.sleep(1)
    rpc_client_2 = cl.Client(settings)
    data = rpc_client_2.get_result(result_id=result_id, timeout=timeout)
    if data:
        cmn.lg.debug("Client 2 received data for result {0}: {1}".format(
            result_id, data
        ))
    else:
        cmn.lg.debug(
            "Client 2 did not receive data for result {0} in time".format(
                result_id
            )
        )


def client_runner():
    """syrpc Client runner routine"""
    client(runner=True, timeout=None)


def run_client(rpc_client, timeout, sleep, num_requests=1):
    """Runs client"""
    type_ = 'ping'
    data = [{'foo': 'bar'}, {'baz': 9001}]
    result_ids = [
        rpc_client.put_request(
            type_=type_, data=data
        ) for _ in range(num_requests)
    ]
    if sleep:
        time.sleep(0.5)
    for result_id in result_ids:
        data = rpc_client.get_result(result_id=result_id, timeout=timeout)
        if data:
            cmn.lg.debug("Client received data for result {0}: {1}".format(
                result_id, data
            ))
        else:
            cmn.lg.debug(
                "Client did not receive data for result {0} in time".format(
                    result_id
                )
            )
