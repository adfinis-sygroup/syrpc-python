# -*- coding: UTF-8 -*-

"""RPC client implementation for SyMonitoring RPC middleware"""

# System imports
import json
import kombu
import socket
import uuid

# Project imports
import syrpc.rpc_base as base
import syrpc.common   as cmn


class Client(base.RPCBase):
    """Class for communicating with RabbitMQ over the AMQP."""

    def __init__(self, settings):
        super(Client, self).__init__(settings)
        self.consumer = kombu.Consumer(
            channel=self.result_channel,
            callbacks=[self.on_result],
            auto_declare=False,
        )

    def put_request(self, type_, data):
        """Sends request with given type and data to AMQ."""
        result_id = uuid.uuid4()
        body = {
            'result_id': str(result_id),
            'type_':     type_.strip(),
            'data':      data
        }
        self.request_queue.put(
            message=body,
        )
        cmn.lg.debug(
            "Client put request for result %s "
            "on %s" % (result_id, self.request_queue)
        )
        return result_id

    def get_result(self, result_id, timeout=None):
        """Tries to get a result, blocks until a request arrives or timeout was
        hit.
        """
        routing_key   = str(result_id)
        hash_id       = cmn.get_hash(routing_key, self.amq_num_queues)
        result_queue = self.get_result_queue(index=hash_id)
        self.wait_id  = routing_key
        self.consumer.add_queue(result_queue)
        cmn.lg.debug("Queue %s in queues: %s" % (
            result_queue, len(self.consumer.queues)
        ))
        self.consumer.consume()
        cmn.lg.debug(
            "Client waiting for result for "
            "request %s on %s during %ss" % (
                hash_id, result_queue, timeout
            )
        )
        while self.response is None:
            try:
                self.amq_connection.drain_events(timeout=timeout)
            except socket.timeout:
                cmn.lg.error("Client hit the fan after %ss" % timeout)
                return None

        cmn.lg.debug("Client got %s from AMQ" % result_id)
        cmn.lg.debug("Client returning %s" % self.response)
        res = self.response
        self.response = None
        return res

    def on_result(self, body, message):
        """Handles the reception of a result over AMQ."""
        cmn.lg.debug("Client received %s/%s" % (body, message))
        message_body = message.body.decode(message.content_encoding)
        body = json.loads(message_body, message.content_encoding)
        if self.wait_id == body['result_id']:
            cmn.lg.debug("Client received %s" % self.wait_id)
            self.response = body
            message.ack()
            self.consumer.queues = []
        else:
            cmn.lg.warn(
                "Client received a wrong result %s" % body['result_id']
            )
            message.reject(requeue=True)
            self.response = None
