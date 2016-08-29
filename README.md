JiyuuBot
========

JiyuuBot is a library and a coordinating daemon aimed at making it easier to
write automated [Telepathy] clients. The source tree is split up into several
components:

 * `src/libtp`: libtp is a thin wrapper around Telepathy's DBus API.
   Telepathy-GLib is cumbersome and complicated, with many of the cool features
   it provides not being of any use to JiyuuBot.  
   Please note that libtp does not aim to expose the full Telepathy spec, but
   rather only the subset of API required by JiyuuBot.

 * `src/libjiyuubot`: This library aims to implement a lot of the basic client
   logic, allowing the code of clients themselves to avoid being bogged down in
   things like command parsing and whatnot.

 * `src/jiyuubot`: The JiyuuBot daemon is the go-between for Telepathy DBus
   services and JiyuuBot clients. It handles things like connections, client
   activation, message relaying, etc.  
   This directory also contains an application called `jiyuubot-launcher` which
   handles setting up a new DBus daemon separate from the user's session bus;
   this allows JiyuuBot to be run without interfering with running chat
   programs.

 * `src/clients`: This is where a set of JiyuuBot clients live. JiyuuBot clients
   are similar in concept to [Telepathy clients], the difference being that
   Telepathy clients handle channels of communication whereas JiyuuBot clients
   handle individual messages. This distinction has a couple of benefits:

    * JiyuuBot clients are free to fall over without impacting service
      availability; they are simply started up again on the next message via
      DBus activation.

    * JiyuuBot clients don't have to participate with Telepathy's transactions
      directly. Things like channel handling and message acknowledgement are all
      handled transparently by the daemon.

Putting all this together yields a resilient chat bot infrastructure capable of
servicing [tens][tp-protos] [of][tp-haze] [protocols][tp-cms], including SMS
message support via [telepathy-ofono][tp-ofono].

[Telepathy]: https://telepathy.freedesktop.org/wiki/
[Telepathy clients]: https://telepathy.freedesktop.org/doc/book/sect.channel-dispatcher.clients.html
[tp-protos]: https://telepathy.freedesktop.org/wiki/Documentation/Protocols_Support/
[tp-haze]: https://developer.pidgin.im/wiki/TelepathyHaze
[tp-cms]: https://telepathy.freedesktop.org/wiki/Components/#connectionmanagers
[tp-ofono]: https://code.launchpad.net/telepathy-ofono


## TODO

Currently, JiyuuBot is versioned 0.3 to indicate the tree is in a prerelease
state. This is a list of some of the things that have to be done before 3.0:

 * Tests. Lots more tests
    * Check the accuracy of DBus bindings
    * Start testing the daemon code
    * Test libjiyuubot base clients
    * Possibly introduce tests for clients themselves
    * Ensure GI bindings install and work properly
 * Document library interfaces
 * Client shutdown timeout
 * Real configuration, instead of current stopgap
 * Automatic client/service reload
 * Resolve sender handles to display names
 * Add more base clients to libjiyuubot (regex, URL handlers, etc)
 * Add more client implementations (github, youtube, etc)
 * Implement Telepathy approver client
 * Improved logging
 * Systemd unit files
 * spec file + copr repo
