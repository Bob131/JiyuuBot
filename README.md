JiyuuBot
==========

An IRC frontend for MPD. See requirements.txt for dependencies. Requires Python 3.

JiyuuBot is a modular IRC bot which exposes an [MPD](http://musicpd.org/) interface to loaded modules. To get yourself up and running, simply create your config file and run:

```
~/JiyuuBot $ mv configs/global.json.example configs/global.json
~/JiyuuBot $ vim configs/global.json
# configure to your liking
~/JiyuuBot $ ./main.py
```

Care should be taken to ensure that _all_ required dependencies are installed, as modules can import at runtime. See below:

```
~/JiyuuBot $ find | xargs grep "import requests" 2> /dev/null
./modules/4chan.py:    import requests
./modules/wiki.py:    import requests
./modules/youtube.py:        import requests
./modules/git.py:            import requests
./modules/git.py:    import requests
./modules/isup.py:    import requests
```

Note that JiyuuBot at this point in time logs *everything*, and these logs can rapidly grow in size. If you're short on disk space, consider disabling logging in your configuration file.

JiyuuBot core code and all modules are licensed under the AGPLv3.