# -*- coding: UTF-8 -*-

"""RPC server implementation for SyMonitoring RPC middleware"""

# System imports
import amqp.exceptions           as aexcept
import kombu

# Project imports
import syrpc.rpc_base as base
import syrpc.common   as cmn


class EmptyException(Exception):
    """Timeout was reached before the server sent an answer"""
    pass


class QueueNotFoundException(Exception):
    """The requested queue does not exist"""
    pass


class Server(base.RPCBase):
    """Class for communicating with RabbitMQ over the AMQP."""

    def __init__(self, settings):
        super(Server, self).__init__(settings)
        self.producer = kombu.Producer(
            self.result_channel,
            exchange=self.result_exchange,
            auto_declare=False,
        )

    def get_request(self, timeout=None):
        """Gets a request and processes it

        Blocks until a request arrives or timeout was hit.
        """
        cmn.lg.debug("Server waiting for requests during %ss" % timeout)
        try:
            message = self.request_queue.get(block=True, timeout=timeout)
        except self.request_queue.Empty:
            raise EmptyException()
        except aexcept.NotFound as e:
            cmn.lg.critical("Server did not find queue: %s" % e)
            raise QueueNotFoundException("Server did not find queue: %s" % e)
        cmn.lg.debug("Server received a request")
        message.ack()
        message   = message.decode()
        result_id = message['result_id']
        data      = message['data']
        type_     = message['type_']
        return (type_, result_id, data)

    def put_result(self, result_id, data):
        """Puts a result of a request to result database and sends it to
        AMQ."""
        routing_key  = str(result_id)
        hash_id      = cmn.get_hash(routing_key, self.amq_num_queues)
        result_queue = self.get_result_queue(index=hash_id)
        body         = {
            'result_id': routing_key,
            'data':      data,
        }
        self.producer.publish(
            body=body,
            routing_key=str(hash_id),
            exchange=self.result_exchange,
            declare=[result_queue],
        )
        cmn.lg.debug(
            "Server published result %s within %s" % (
                routing_key,
                result_queue,
            )
        )
