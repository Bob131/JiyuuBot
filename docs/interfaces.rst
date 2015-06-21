Writing interfaces
==================

An example interface
^^^^^^^^^^^^^^^^^^^^
Start by creating a new file in the interfaces folder:

::

    $ vim interfaces/example.py

Import the required machinery and register:

.. code-block:: python

    from . import BaseInterface, register

    @register
    class GenericExample(BaseInterface):
        pass

Implement required functions:

.. code-block:: python

    import socket
    from . import BaseInterface, register, recv_queue

    @register
    class GenericExample(BaseInterface):
        MANDATORY_CONFIG_OPTIONS = ["host"]

        def init_hooks(self):
            self.s = socket.socket()
            self.print("Connecting to {}".format(self.config["host"]))
            self.s.connect((self.config["host"], 1234))

        def recv(self):
            while True:
                original = self.s.recv().decode("UTF-8").strip()
                print("{} <<< {}".format(self.id, line))
                msg = {
                    "raw": original,
                    "id": self.id,
                    "iface": self.__class__.__name__
                }
                recv_queue.put(msg)

        def send(self):
            while True:
                msg = self.send_queue.get(True)
                print("{} >>> {}".format(self.id, msg.strip()))
                self.s.send(bytes(msg, "UTF-8"))

Thats it! However, as it is it will only respond to modules who have
registered as `raw_handlers` since the message dictionary we put on
the queue in `recv()` doesn't have a `msg` attribute. This attribute
is a parsed version of the message that allows generic modules to handle
the plain text message without needing knowledge of the underlying protocol.

While we're at it, we should also add a generic `queue()` function to
allow those same generic modules to send messages to where they have to
go:

.. code-block:: python

    import socket
    from . import BaseInterface, register, recv_queue

    @register
    class GenericExample(BaseInterface):
        MANDATORY_CONFIG_OPTIONS = ["host"]

        def init_hooks(self):
            self.s = socket.socket()
            self.print("Connecting to {}".format(self.config["host"]))
            self.s.connect((self.config["host"], 1234))

        def send(self):
            while True:
                msg = self.send_queue.get(True)
                print("{} >>> {}".format(self.id, msg.strip()))
                self.s.send(bytes(msg, "UTF-8"))

        def recv(self):
            while True:
                original = self.s.recv().decode("UTF-8").strip()
                print("{} <<< {}".format(self.id, line))
                msg = {
                    "raw": original,
                    "id": self.id,
                    "iface": self.__class__.__name__
                    "msg": original # this made-up protocol sure is convenient!
                }
                recv_queue.put(msg)

        def queue(self, text, destination):
            self.queue_raw("Hey {}! {}".format(destination, text))


`interfaces` documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: interfaces
   :members: main, recv_queue, register

.. autoclass:: BaseInterface
   :members:
