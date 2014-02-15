JiyuuBot
==========

An IRC frontend for MPD. Depends on python-mpd2.

There needs to be a folder in your music path called "[nick]\_intros" containing audio clips to be played every so often

### CentOS 6 Setup Guide ###
1. Ensure that [RPMForge](http://wiki.centos.org/AdditionalResources/Repositories/RPMForge) and [EPEL](https://fedoraproject.org/wiki/EPEL) repos are configured
2. Install MPD  
 At the time of writing (2014-01-07), CentOS 6.5 does not support the minimum required version of Glib by MPD 0.18 and the newest version available in the repos has some bugs which makes streaming difficult. For this reason, instructions on compiling v0.17.6 follow  
 1. Install prerequisites  
  ```yum install wget libid3tag-devel libsamplerate-devel libcurl-devel ffmpeg-devel flac-devel libmad-devel libshout-devel libsndfile-devel wavpack-devel```
 2. Get the MPD source  
  ```wget http://www.musicpd.org/download/mpd/0.17/mpd-0.17.6.tar.gz```  
  ```tar -xvf mpd*```
 3. Configure and build  
  ```cd mpd-0.17.6```  
  ```./configure --enable-curl --enable-ffmpeg --enable-id3 --enable-lsr --enable-sndfile --enable-wavpack --enable-flac --enable-httpd-output --enable-lame-encoder --enable-mad --enable-pipe-output --enable-shout --enable-vorbis --enable-vorbis-encoder```  
  ```make && make install```
  
3. Install the MPD-Python bindings

 ```sh
  yum install python-pip
  pip install python-mpd2
 ```
4. Create MPD user and create associated directories

 ```sh
 useradd -d /var/lib/mpd -m -s /sbin/nologin mpd
 mkdir /var/lib/mpd/playlists /var/lib/mpd/music
 chown -R mpd /var/lib/mpd
 ```

5. Write MPD config

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

6. Start MPD

 ```sh
  /usr/bin/mpd
 ```
 
7. Clone the repo and configure

 ```sh
  git clone https://github.com/SlashGeeSlashOS/JiyuuRadio.git
  cd JiyuuRadio
  mv configs/config.py.example configs/config.py
  vi configs/config.py
 ```

8. Start the bot

 ```sh
  python ./main.py &
 ```


Optionally, configure your HTTP daemon to reverse proxy on behalf of the JSON server in JiyuuRadio
