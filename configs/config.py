MPD_HOST = "127.0.0.1" # MPD server
MPD_PORT = 6600 # MPD port, 6600 default

HOST = "irc.rizon.net" # IRC server
HOME_CHANNEL = "#JiyuuRadio" # IRC Channel
NICK = "JiyuuRadio" # IRC Nick
PORT = 9999 # IRC port, often 9999 for SSL
SSL = True # Use SSL connction?

MUSIC_PATH = "/media/music/Music" # Music folder used by MPD

TESTING = False # Sets special testing settings

if TESTING:
    NICK += "Test"
    HOME_CHANNEL = "#BotPlayground"
