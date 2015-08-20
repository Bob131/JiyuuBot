Writing interfaces
==================

This document describes the creation of a custom interface for JiyuuBot
modules. As JiyuuBot's primary interface is for Internet Relay Chat, some
of the functions described below are done so from that perspective. A
quick primer on IRC terminology might be of assistance for the
uninitiated.

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
the queue in `recv()` doesn't have `msg` and `dest` attributes:

 * `msg` is a parsed version of the message that allows generic modules
   to handle the plain text message without needing knowledge of the
   underlying protocol.
 * `dest` tags a message so we know where it's going. For example, in
   the IRC interface the `dest` attribute is usually an IRC channel.

.. warning:: The `dest` attribute shouldn't reveal where the incoming
             message comes from, but rather where the reply messages
             should be going.

Some other attributes of note are:

 * `src`: Where the incoming message originates, eg an IRC nick.
 * `tag`: Some extra information about `src`. An example from the IRC
   interface might look like `Bob131!~Bob131@Rizon-11D33CFA.bob131.so`.

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
                    "iface": self.__class__.__name__,
                    "dest": None,
                    "msg": original # this made-up protocol sure is convenient!
                }
                recv_queue.put(msg)

        def queue(self, text, _):
            self.queue_raw(text)

In the example above, we've just ignored the destination attribute
completely. In most cases, modules will send reply messages to the same
destination specified in the incoming message dictionary (the result of
which will have the effect of `_` in `queue()` always being `None` in our
example). This means that `dest` shouldn't really be where the imcoming
message came from, but rather where the outgoing message should go. This
distinction is important when considering the difference between a
message exchange in an IRC chan and a message exchange directly between
a user and the bot.


`interfaces` documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: interfaces
   :members: recv_queue, register

.. autoclass:: BaseInterface
   :members:
