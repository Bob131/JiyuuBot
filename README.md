JiyuuRadio
==========

An IRC frontend for MPD. Depends on python-mpd2.

There needs to be a folder in your music path called "[nick]\_intros" containing audio clips to be played every so often

### CentOS 6 Setup Guide ###
1. Ensure that [RPMForge](http://wiki.centos.org/AdditionalResources/Repositories/RPMForge) and [EPEL](https://fedoraproject.org/wiki/EPEL) repos are configured
2. Install MPD and the MPD-Python bindings

 ```sh
  yum install mpd python-pip
  pip install python-mpd2
 ```
3. Create MPD user and create associated directories

 ```sh
 useradd -d /var/lib/mpd -m -s /sbin/nologin mpd
 mkdir /var/lib/mpd/playlists /var/lib/mpd/music
 chown -R mpd /var/lib/mpd
 ```

4. Write MPD config

 ```sh
  echo "music_directory         \"/var/lib/mpd/music\"
  playlist_directory      \"/var/lib/mpd/playlists\"
  db_file                 \"/var/lib/mpd/database\"
  log_file                \"/var/lib/mpd/log\"
  state_file              \"/var/lib/mpd/state\"
  user                    \"mpd\"
  bind_to_address         \"127.0.0.1\"
  bind_to_address         \"/var/lib/mpd/socket\"
  port                    \"6600\"
  audio_output {
      #shout/http output info
  }
  buffer_before_play      \"100%\"" >> /etc/mpd.conf
 ```

5. Start MPD

 ```sh
  /usr/bin/mpd
 ```
 
6. Clone the repo and configure

 ```sh
  git clone https://github.com/SlashGeeSlashOS/JiyuuRadio.git
  cd JiyuuRadio
  vi configs/config.py
 ```

7. Start the bot

 ```sh
  python ./main.py &
 ```
