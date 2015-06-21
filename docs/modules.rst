Writing modules
===============

An example module
^^^^^^^^^^^^^^^^^

Start by creating a new file in the modules folder:

::

    $ vim modules/example.py

Lets try creating a new command. Import the required machinery and our
command:

.. code-block:: python

    from . import command, send

    @command
    def hello(msg):
        send("Hello!")

We might want to add some aliases and a help message:

.. code-block:: python

    from . import command, send

    @command("hi")
    def hello(msg):
        """.hello - say hi!"""
        send("Hello!")

Great! Now we'll be run whenever someone in a chatroom that JiyuuBot
services types ".hello" or ".hi", they'll get a cute response.
The inclusion of this docstring also means we've been added to the list
of commands shown by ".help" and our docstring will be shown on ".help
hello".

Lets suppose we want to respond differently depending on how we're
invoked. We can do that by accessing the msg parameter:

.. code-block:: python

    from . import command, send

    @command("hi")
    def hello(msg):
        """.hello - say hi!"""
        # get the first word and remove the leading '.'
        cmd = msg["msg"].split(" ")[0][1:]
        if cmd == "hi":
            send("Hello!")
        elif cmd == "hello":
            send("Hey!")

But it seems this still isn't enough for our needs! We need to respond
to people saying hello whenever!

Lets start by putting our what-to-say logic in a new function:

.. code-block:: python

    from . import functions, command, send

    @functions
    def how_to_hello(cmd):
        if cmd == "hi":
            return "Hello!"
        elif cmd == "hello":
            return "Hey!"

    @command("hi")
    def hello(msg):
        cmd = msg["msg"].split(" ")[0][1:]
        send(functions.how_to_hello(cmd))

This way if any other module needs our `how_to_hello` function, they can
access it the same way.

Now lets add regex handling:

.. code-block:: python

    import re
    from . import functions, regex_handler, command, send

    @functions
    def how_to_hello(cmd):
        if cmd == "hi":
            return "Hello!"
        elif cmd == "hello":
            return "Hey!"

    @command("hi")
    def hello(msg):
        cmd = msg["msg"].split(" ")[0][1:]
        send(functions.how_to_hello(cmd))

    @regex_handler(".*[^a-z]hello[^a-z].*")
    @regex_handler(".*[^a-z]hi[^a-z].*")
    def hello(msg):
        cmd = re.match(".*[^a-z](hi|hello)[^a-z].*").group(0)
        send(functions.how_to_hello(cmd))

Since regex matching is done with the `IGNORECASE` flag, this is all we
need.


Handling raw messages
^^^^^^^^^^^^^^^^^^^^^

Modules can also be used to handle raw messages from interfaces. See the
below excerpt from `modules/multichan.py`:

.. code-block:: python

    from . import get_interface, raw_handler, subscribe

    @subscribe("IRC")
    @raw_handler
    def invite(msginfo):
        if get_interface().get_command(msginfo["raw"]) == "INVITE":
            chan = msginfo["raw"][msginfo["raw"].index(" :")+2:]
            get_interface().join_irc(chan)

This snippet makes use of `subscribe()` to ensure it only receives
messages from IRC interfaces and registers it's existence with
`raw_handler()`.

It then uses `get_interface()` to get a reference to the interface
instance which received the message being handled and calls `get_command()`
(a method specific to the IRC interface) to decide what to do.


`modules` documentation
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: modules
   :members: 
