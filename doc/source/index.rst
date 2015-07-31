.. SyRPC documentation master file, created by
   sphinx-quickstart on Fri Jul 31 15:49:01 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SyRPC - RPC for stateless backends
==================================

SyRPC supports stateless backends using result_id.

::

      ____   __ 
     |    | |==|
     |____| |  | Web Client
     /::::/ |__|
      |
      |   http get /        .-----------------------.
      |-------------------->|      Backend(0)       |
      |                     | put_request(          |         .-------------------.
      | rendered page       |    'echo',            |         |      Server       |
      | including result_id |    {'value': 'hello'} |-------->| (                 |
      |<--------------------| )                     |         |     type_,        |
      |                     '-----------------------'         |     result_id,    |
      |                                                       |     data          |
      |                                                       | ) = get_request() |
      |    ajax get /echo   .-----------------------.         |                   |
      |-------------------->|      Backend(1)       |-------->| put_request(      |
      |                     | get_result(result_id) |         |     result_id,    |
      |    echo data        |                       |         |     data          |
      |<--------------------|                       |<--------| )                 |
      |                     '-----------------------'         |                   |
      |                                                       '-------------------'
      v

Collisions on the queues (too many rejects) are reduced by using a hash-table
of queues, by default 64 queues. The hash module 64 of the result_id is used to
identify the result_queue. This makes SyRPC 12 compatible with 12 Factor
Applications but has still quite good performance.

Example Echo Server
-------------------

.. code:: python

   import syrpc
   rpc_server =  syrpc.Server({
       'app_anme': 'syrpc',
       'amq_host': 'localhost',
   })
   (type_, result_id, data) = rpc_server.get_request()
   cmn.lg.info("Server received request: %s" % (result_id))
   if type_ == 'echo':
       rpc_server.put_result(
           result_id=result_id, data=data
       )

Example Echo Client
-------------------

.. code:: python

   import syrpc
   rpc_client =  syrpc.Client({
       'app_anme': 'syrpc',
       'amq_host': 'localhost',
   })
   type_ = 'echo'
   data = [{'foo': 'bar'}, {'baz': 9001}]
   result_id = rpc_client.put_request(
       type_=type_, data=data,
   )
   result = rpc_client.get_result(result_id=result_id)

.. automodule:: syrpc
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

