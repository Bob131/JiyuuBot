Writing modules
===============

An example module
^^^^^^^^^^^^^^^^^

Start by creating a new file in the modules folder:

::

    $ vim modules/example.py

Lets try creating a new regex handler. Import the required machinery and
create our handler:

.. code-block:: python

    from . import regex_handler, send

    @regex_handler(".*\\bhi\\b.*")
    def hello(msg):
        send("Hello!")

.. NOTE:: Regex matching is done with the `IGNORECASE` flag, so this will
          match "hi," "HI," "hI" etc

This will fire off a cute "Hello!" to any message received containing
"hi". Don't worry if this appears a little daunting, there are some
methods below which makes things a little easier.

The `modules` package contains an object which allows modules to export
functions. This object (unsurprisingly) is called `functions`. Here it is
in action:

.. code-block:: python

    from . import regex_handler, send, functions

    @functions
    def how_to_hello(msg):
        if "hi" in msg.lower():
            return "Hiya!"
        else:
            return "Yo~"

    @regex_handler(".*\\bhi\\b.*")
    @regex_handler(".*\\bhellow\\b.*")
    def hello(msg):
        send(functions.how_to_hello(msg['msg']))

For more info on what kind of information you can expect in the `msg`
argument, check out the interface writing docs.

Writing UI via the `regex_handler` decorator is error prone and hardly
concise. Luckily, there are modules who export functions to make our
job a little easier. Have a look:

.. code-block:: python

    from . import send, functions

    @functions.command
    def hello():
        send("Hey!")

Now if you send your JiyuuBot instance ".hello," it will respond in kind.
We can even add aliases and a help message:

.. code-block:: python

    @functions.command("hi")
    def hello():
        """.hello - Say hi!"""
        send("Hey!")

Now our command will be executed on ".hello" or ".hi" and will appear in
the list produced by ".help".



Handling raw messages
^^^^^^^^^^^^^^^^^^^^^

Modules can also be used to handle raw messages from interfaces. See the
below excerpt from `modules/irc.py`:

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
