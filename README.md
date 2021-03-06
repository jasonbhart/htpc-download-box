# HTPC (mini) Download (Seed) Box for Single-Board Computers (like the Raspberry Pi and Odroid) 

Sonarr / Radarr / NZBHydra2 / Jackett / NZBGet / Deluge / OpenVPN / Traefik / Portainer

TV shows and movies download, sort, with the desired quality and subtitles, behind a VPN (optional), ready to watch, in a beautiful media player.
All automated.

## Table of Contents

- [HTPC Download Box](#htpc-download-box)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Monitor TV shows/movies with Sonarr and Radarr](#monitor-tv-showsmovies-with-sonarr-and-radarr)
    - [Search for releases automatically with Usenet and torrent indexers](#search-for-releases-automatically-with-usenet-and-torrent-indexers)
    - [Handle bittorrent and usenet downloads with Deluge and NZBGet](#handle-bittorrent-and-usenet-downloads-with-deluge-and-nzbget)
    - [Organize libraries, fetch subtitles and play videos with Plex](#organize-libraries-fetch-subtitles-and-play-videos-with-plex)
  - [Hardware configuration](#hardware-configuration)
  - [Software stack](#software-stack)
  - [Installation guide](#installation-guide)
    - [Introduction](#introduction)
    - [Install docker and docker-compose](#install-docker-and-docker-compose)
    - [Setup Deluge](#setup-deluge)
      - [Docker container](#docker-container)
      - [Configuration](#configuration)
    - [Setup a VPN Container](#setup-a-vpn-container)
      - [Introduction](#introduction)
      - [privateinternetaccess.com custom setup](#privateinternetaccesscom-custom-setup)
      - [Docker container](#docker-container)
    - [Setup Jackett](#setup-jackett)
      - [Docker container](#docker-container)
      - [Configuration and usage](#configuration-and-usage)
    - [Setup NZBGet](#setup-nzbget)
      - [Docker container](#docker-container)
      - [Configuration and usage](#configuration-and-usage)
    - [Setup Plex](#setup-plex)
      - [Media Server Docker Container](#media-server-docker-container)
      - [Configuration](#configuration)
      - [Download subtitles automatically with sub-zero](#download-subtitles-automatically-with-sub-zero)
      - [Setup Plex clients](#setup-plex-clients)
    - [Setup Sonarr](#setup-sonarr)
      - [Docker container](#docker-container)
      - [Configuration](#configuration)
      - [Give it a try](#give-it-a-try)
    - [Setup Radarr](#setup-radarr)
      - [Docker container](#docker-container)
      - [Configuration](#configuration)
      - [Give it a try](#give-it-a-try)
      - [Movie discovering](#movie-discovering)
  - [Manage it all from your mobile](#manage-it-all-from-your-mobile)
  - [Going Further](#going-further)

## Overview

This is what I have set up at home to handle TV shows and movies automated download, sort and play.

*Disclaimer: I'm not encouraging/supporting piracy, this is for information purpose only.*

How does it work? I rely on several tools integrated together. They're all open-source, and deployed as Docker containers on my Linux server.

The common workflow is detailed in this first section to give you an idea of how things work.

### Monitor TV shows/movies with Sonarr and Radarr

Using [Sonarr](https://sonarr.tv/) Web UI, search for a TV show by name and mark it as monitored. You can specify a language and the required quality (1080p for instance). Sonarr will automatically take care of analyzing existing episodes and seasons of this TV show. It compares what you have on disk with the TV show release schedule, and triggers download for missing episodes. It also takes care of upgrading your existing episodes if a better quality matching your criterias is available out there.

![Monitor Mr Robot season 1](img/mr_robot_season1.png)
Sonarr triggers download batches for entire seasons. But it also handle upcoming episodes and seasons on-the-fly. No human intervention is required for all the episodes to be released from now on.

When the download is over, Sonarr moves the file to the appropriate location (`my-tv-shows/show-name/season-1/01-title.mp4`), and renames the file if needed.

![Sonarr calendar](img/sonarr_calendar.png)

[Radarr](https://radarr.video) is the exact same thing, but for movies.

### Search for releases automatically with Usenet and torrent indexers

Sonarr and Radarr can both rely on two different ways to download files:

- Usenet (newsgroups) bin files. That's the historical and principal option, for several reasons: consistency and quality of the releases, download speed, indexers organization, etc. Often requires a paid subscription to newsgroup servers.
- Torrents. That's the new player in town, for which support has improved a lot lately.

I'm using both systems simultaneously, torrents being used only when a release is not found on newsgroups, or when the server is down. At some point I might switch to torrents only, which work really fine as well.

Files are searched automatically by Sonarr/Radarr through a list of  *indexers* that you have to configure. Indexers are APIs that allow searching for particular releases organized by categories. Think browsing the Pirate Bay programmatically. This is a pretty common feature for newsgroups indexers that respect a common API (called `Newznab`).
However this common protocol does not really exist for torrent indexers. That's why we'll be using another tool called [Jackett](https://github.com/Jackett/Jackett). You can consider it as a local proxy API for the most popular torrent indexers. It searches and parse information from heterogeneous websites.

![Jackett indexers](img/jackett_indexers.png)

The best release matching your criteria is selected by Sonarr/Radarr (eg. non-blacklisted 1080p release with enough seeds). Then the download is passed on to another set of tools.

### Handle bittorrent and usenet downloads with Deluge and NZBGet

Sonarr and Radarr are plugged to downloaders for our 2 different systems:

- [NZBGet](https://nzbget.net/) handles Usenet (newsgroups) binary downloads.
- [Deluge](http://deluge-torrent.org/) handles torrent download.

Both come with a nice Web UI, making them perfect candidates for being installed on a server. Sonarr & Radarr already have integration with these clients, meaning they rely on each service's API to request a download, status and handle finished downloads.

Both are very standard and popular tools. I'm using them for their integration with Sonarr/Radarr but also as standalone downloaders for everything else.

For security and anonymity reasons, I'm running Deluge behind a VPN connection. All incoming/outgoing traffic from deluge is encrypted and goes out to an external VPN server. Other services run on the local network. This is done through Docker networking stack (more to come on the next paragraphs).

## Hardware configuration

I'm using an [Odroid C2](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G145457216438) (4 cores, 1.50GHz, arm8, 2GB RAM), with a 4TB USB disk for data.

You can also use a Raspberry Pi3B, although performance will be a downgrade since the OS is 32bit and it only has 1GB of RAM. I have included a version of the Docker Compose file for this platform as well. 

Your USB storage options may have additional power requirements then can be services by the default SBC (Single-board computer) power supply. This will be especially true with mechanical hard drive units (vs SSD) without their own dedicated power supply.  You may need to get a more powerful SBC power supply (3A-4A) or a powered USB hub to connect your storage devices.

You may also have a desire to keep these drives in NTFS format to allow for connecting them directly to a Windows computer on occasion for direct access to downloaded media.  While there are drivers for Linux (NTFS-3G) which will facilitate this, I have found them to be unreliable in cases where very large files are being manipulated (such as here).  Additionally, if you start to have occasional power problems, caused by a power hungry drive, this driver doesn't handle failed writes very gracefully.  I suggest formatting the drive with ext4 (the native Ubuntu file format) and then use Samba (over the network) to access the files from Windows.  

## Networking setup
To make management easy I have used the DHCP reservation feature on my internet router/modem to give the same IP address to server everytime. This makes it easier to connect to it via SSH, but also allows for port forwarding rules to be setup on the router to work with Traefik reverse proxy.  

You may want to make another DHCP reservation for the computer which is running Plex Media Server, so Sonarr and Radarr can update Plex with metadata about newly downloaded files.  This will allow you to setup the Plex integration settings in Sonarr and Radarr using the IP address of this other computer.

Port forwarding on the router should be setup on 2 different ports (I picked 6660 and 6661) to forward traffic from the outside world to the reverse proxy daemon on the seed/download box.  

## System setup

I'm running the latest Ubuntu port provided by the Odroid manufacturer.  Make sure you run apt-get update/upgrade prior to installing anything else.

I have also installed 'screen' to allow keeping an 'admin' session logged in running top, should that be needed.

I also encourage the installation of UFW (uncomplicated firewall) via apt-get.  To use with Docker you will need to follow these instructions: (https://www.techrepublic.com/article/how-to-fix-the-docker-and-ufw-security-flaw/). After installation, open ports for:
- SSH
- 80/tcp (Heimdall HTTP)
- 443/tcp (Heimdall HTTPS)
- 8112/tcp (Deluge)
- 6789/tcp (NZBGet)
- 8989/tcp (Sonarr)
- 7878/tcp (Radarr)
- 5076/tcp (NZBHydra2)
- 9117/tcp (Jackett)
- 9000/tcp (Portainer)
- 445/tcp (Samba)                  
- 139/tcp (Samba)                 
- 138/udp (Samba)                 
- 137/udp (Samba)
- 6660/tcp (Traefik unencripted; can be changed)
- 6661/tcp (Traefik encripted; can be changed)

## Docker
The easiest way to install Docker is by using the command (do this as root):
`curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh`

You must install Python PIP to install Docker Compose.
`sudo apt-get install python-pip`

Make sure docker works fine:
`docker run hello-world`

`sudo python -m pip install docker-compose`

## Software stack

![Architecture Diagram](img/architecture_diagram.png)

**Downloaders**:
- [Deluge](http://deluge-torrent.org): torrent downloader with a web UI
- [NZBGet](https://nzbget.net): usenet downloader with a web UI

**Search**:
- [Jackett](https://github.com/Jackett/Jackett): API to search torrents from multiple indexers
- [NZBHydra2](https://github.com/theotherp/nzbhydra2): API to search nzbs from multiple indexers

**Download orchestration**:
- [Sonarr](https://sonarr.tv): manage TV shows to watch for, automatic downloads, sort & rename
- [Radarr](https://radarr.video): basically the same as Sonarr, but for movies

**VPN**:
- [OpenVPN](https://openvpn.net/) client configured with [Private Internet Access](https://www.privateinternetaccess.com/) access for torrent traffic ONLY

**Reverse Proxy**:
- [Traefik](https://github.com/containous/traefik): allows selective and secured external internet access to the various tools 

**Docker continer management**:
- [Portainer](https://github.com/portainer/portainer): provides Docker management GUI incase of emergency 

**Media Center (optional)**:
- [Plex](https://plex.tv): media center server with streaming transcoding features, useful plugins and a beautiful UI. Clients available for a lot of systems (Linux/OSX/Windows, Web, Android, Chromecast, Android TV, etc.) NOTE: not included by default in docker-compose files due to resource constraints of single board computers (RAM and processing power for transcoding); suggest installing this on a different PC and mapping network drives to the seedbox folders via Samba.

## Installation guide

### Introduction

The idea is to set up all these components as Docker containers in a `docker-compose-*.yml` file.
We'll reuse community-maintained images (special thanks to [linuxserver.io](https://www.linuxserver.io/) for many of them).
I'm assuming you have some basic knowledge of Linux and Docker.

The stack is not really plug-and-play. You'll see that manual configuration is required for most of these tools. Configuration is not fully automated (yet?), but is persisted on reboot. Some steps also depend on external accounts that you need to set up yourself (usenet indexers, torrent indexers, vpn server, plex account, etc.). We'll walk through it.

Optional steps described below that you may wish to skip:

- Using newsgroups (Usenet): you can skip NZBGet installation and all related Sonarr/Radarr indexers configuration if you wish to use torrents only.

### Local environment file

We will be referencing local environment variables which are set in a text file named `.env`, residing in the same folder as the docker-compose files. The file should be similar to:
```.env
PUID=1000
PGID=1000
TZ=America/Los_Angeles
DOMAINNAME=change-me.com
```
I am assuming you are installing this onto a fresh installation where the user running everything is the first user created on this Linux installation.  If not adjust the UUID and GUID to that of the user you will be running the Docker Compose files with.

You will need to change the TZ setting to match your Linux timezone string which matches your timezone, as well as change the domain name to the one you will use with CloudFlare (or another DNS provider which can accept API calls to update the external IP address of the modem/router). 

### Setup Deluge

#### Docker container

We'll use deluge Docker image from linuxserver, which runs both the deluge daemon and web UI in a single container.

```yaml
    container_name: deluge
    depends_on:
      - vpn
    image: lsioarmhf/deluge-aarch64:latest
    restart: unless-stopped
    network_mode: service:vpn # run on the vpn network
    environment:
      - PUID=${PUID} # default user id, for downloaded files access rights
      - PGID=${PGID} # default group id, for downloaded files access rights
      - TZ=${TZ} # timezone
    volumes:
      - /media/usb1/ongoing/complete:/downloads/complete # download folder
      - /media/usb1/ongoing/incomplete:/downloads/incomplete # download folder
      - /media/usb1/ongoing/torrent-blackhole:/downloads/torrent-blackhole # put .torrent files
      - ${HOME}/.config/deluge:/config # config files
...
```

Things to notice:

- define PUID and GUID with your own user UID and GID (run `id $USER` to get them) in a .env file residing in the same directory as the docker-compose file.
- The network Deluge uses is the same as used for the VPN service. This segregates all traffic from Deluge and forces it over the VPN tunnel. 
- Set both volumes accordingly to your desired setup. I chose to store downloaded files on an external volume, and configuration files in a hidden sub-directory (.config) off my HOME directory.

Then run the container with `docker-compose -f <docker-compose-file-name> up -d`.
To follow container logs, run `docker-compose logs -f deluge`.

#### Configuration

You should be able to login on the web UI (`localhost:8112`, replace `localhost` by your download box ip if needed).

![Deluge Login](img/deluge_login.png)

The default password is `deluge`. You are asked to modify it, I chose to set an easy one since deluge won't be accessible from outside my local network. NOTE: you must set some form of a password or Heimdall will not know to ping Deluge for stats, so just keep it easy to remember and simple to type.

The running deluge daemon should be automatically detected and appear as online, where you can select to connect to it.

![Deluge daemon](img/deluge_daemon.png)

Once you are connected, click on the Prefences button at the top of browser window. From here you will modify several of the default settings. These will persist across reboots after they are changed.

![Deluge paths](img/deluge_path.png)

You may want to change the download directory. I like to have two distinct directories for incomplete (ongoing) downloads, and complete (finished) ones. These paths must be the same as they are set in Radarr and Sonarr or else these tools will not be able to find completed downloads.  This is because Sonarr and Radarr communicate with Deluge via its API and Deluge will notify the requesting tool when a file is completed and ready for import. 

Also, I set up a blackhole directory: every torrent file in there will be downloaded automatically. This is useful for Jackett manual searches. 

If you use Torrents a lot, you may want to activate `autoadd` in the plugins section: it adds supports for `.magnet` files. If you do want to use magnet files, make sure you do not disable 'DHT' in Deluge.

I suggest downloading a 3rd party configuration plugin for Deluge which will allow you to set some parameters which arent easily accesible from the user interface.
These parameters are explained here: [libtorrent manual](https://www.libtorrent.org/tuning.html)

The configuration plugin is available here: [ltConfig](https://github.com/ratanakvlun/deluge-ltconfig/releases)

Download the .egg file and go into Deluge Preferences and select the Plugins Category. Click the Install button and upload the .egg file.

Once installed, a new Preferences Category will appear called 'ltConfig'.  Click the newly added list item and then select 'High Performance Seed' from the drop-down list.  Before hitting 'Apply', scroll down to 'use_read_cache' and put a check in the checkbox to the left of the Name (if one doesn't appear already).  This show now allow you to uncheck the Setting. This keeps RAM usage modest at a slight performance hit.  Without this Deluge can use an excessive amount of RAM and cause a lot of extra overhead caused by swapping. 

One additional setting which was needed for some VPN providers (PIA) is to disable uTP. If you see a large amount of Torrent activity after starting Deluge and then it slows down to nothing, this is the first thing you should try to cure this.  Use the 'ltConfig' plugin to disable 'enable_incoming_utp' and 'enable_outgoing_utp' in the same way as disabled 'use_read_cache' above.

After all settings are as you want, click the Apply button.  Most of these settings will be applied immediately but some may require restarting the container.
 

You can also tweak queue settings, defaults are fairly small. Also you can decide to stop seeding after a certain ratio is reached. That will be useful for Sonarr, since Sonarr can only remove finished downloads from deluge when the torrent has stopped seeding. Setting a very low ratio is not very fair though !

Configuration gets stored automatically in your mounted volume (`${HOME}/.config/deluge`) to be re-used at container restart. Important files in there:

- `auth` contains your login/password
- `core.conf` contains your deluge configuration

You can use the Web UI manually to download any torrent from a .torrent file or magnet hash.

### Setup a VPN Container

#### Introduction

The goal here is to have an OpenVPN Client container running and always connected. We'll make Deluge incoming and outgoing traffic go through this OpenVPN container.

This must come up with some safety features:

1. VPN connection should be restarted if not responsive
1. Traffic should be allowed through the VPN tunnel *only*, no leaky outgoing connection if the VPN is down
1. Deluge Web UI should still be reachable from the local network

Luckily, someone already [set that up quite nicely](https://github.com/dperson/openvpn-client).

Point 1 is resolved through the OpenVPN configuration (`ping-restart` set to 120 sec by default).
Point 2 is resolved through [iptables rules](https://github.com/dperson/openvpn-client/blob/master/openvpn.sh#L52-L87)
Point 3 is also resolved through [iptables rules](https://github.com/dperson/openvpn-client/blob/master/openvpn.sh#L104)

Configuration is explained on the [project page](https://github.com/dperson/openvpn-client), however it is not that easy to follow depending on your VPN server settings.
I'm using a privateinternetaccess.com VPN, so here is how I set it up.

#### privateinternetaccess.com custom setup

*Note*: this section only applies for [PIA](https://privateinternetaccess.com) accounts.

Download PIA OpenVPN [configuration files](https://privateinternetaccess.com/openvpn/openvpn.zip).
In the archive, you'll find a bunch of `<country>.ovpn` files, along with 2 other important files: `crl.rsa.2048.pem` and `ca.rsa.2048.crt`. Pick the file associated to the country you'd like to connect to, for example `swiss.ovpn`.
Copy the 3 files to `${HOME}/.vpn`.
Create a 4th file `auth` with the following content:

```Text
<pia username>
<pia password>
```

You should now have 3 files in `${HOME}/.vpn`:

- swiss.ovpn
- vpn.auth
- crl.rsa.2048.pem
- ca.rsa.2048.crt

Edit `swiss.ovpn` (or any other country of your choice) to tweak a few things (see my comments on lines added or modified):

```INI
client
dev tun
proto udp
remote swiss.privateinternetaccess.com 1198
resolv-retry infinite
nobind
persist-key
# persist-tun # disable to completely reset vpn connection on failure
cipher aes-128-cbc
auth sha1
tls-client
remote-cert-tls server
auth-user-pass /vpn/vpn.auth # to be reachable inside the container
comp-lzo no
verb 1
reneg-sec 0
crl-verify /vpn/crl.rsa.2048.pem # to be reachable inside the container
ca /vpn/ca.rsa.2048.crt # to be reachable inside the container
disable-occ
keepalive 10 30 # send a ping every 10 sec and reconnect after 30 sec of unsuccessfull pings
pull-filter ignore "auth-token" # fix PIA reconnection auth error that may occur every 8 hours
tun-mtu 1400 # set tunnel MTU to smaller than maximum of connection to reduce fragmentation
mssfix 1360 # set size which local vpn client will resize larger frames
sndbuf 393216 # set explicit buffer size 
rcvbuf 393216 # (see https://winaero.com/blog/speed-up-openvpn-and-get-faster-speed-over-its-channel/)
```

#### Docker container

Put it in the docker-compose file, and make deluge use the vpn container network:

```yaml
  vpn:
    container_name: vpn
    image: dperson/openvpn-client:<arch>
    cap_add:
      - net_admin # required to modify network interfaces
    environment:
      - TZ=${TZ} # timezone
      - FIREWALL # setup a firewall to force all outbout traffic across VPN
      - DNS # only use VPN providers dns to prevent DNS query leaks
    tmpfs:
      - /run
      - /tmp
    restart: unless-stopped
    security_opt:
      - label:disable
    stdin_open: true
    tty: true
    volumes:
      - /dev/net/tun:/dev/net/tun:z # tunnel device
      - ${HOME}/.vpn:/vpn # OpenVPN configuration
    ports:
      - 8112:8112 # port for Deluge web UI to be reachable from local network
    command: '-d -r 10.1.10.0/24' # route local network traffic (change to the subnet IP of your local network)
```

Notice how deluge is now using the vpn container network, with deluge web UI port exposed on the vpn container for local network access.

You can check that deluge is properly going out through the VPN IP by using [torguard check](https://torguard.net/checkmytorrentipaddress.php).
Get the torrent magnet link there, put it in Deluge, wait a bit, then you should see your outgoing torrent IP on the website.

![Torrent guard](img/torrent_guard.png)

### Setup Jackett

[Jackett](https://github.com/Jackett/Jackett) translates request from Sonarr and Radarr to searches for torrents on popular torrent websites, even though those website do not have a sandard common APIs (to be clear: it parses html for many of them :)).

#### Docker container

No surprise: let's use linuxserver.io container !

```yaml
jackett:
    container_name: jackett
    image: linuxserver/jackett:100
    restart: unless-stopped
    network_mode: host
    environment:
      - PUID=1000 # default user id, for downloaded files access rights
      - PGID=1000 # default group id, for downloaded files access rights
      - TZ=Europe/Paris # timezone
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /media/${USER}/data1/downloads/ongoing/torrent-blackhole:/downloads # place where to put .torrent files
      - ${HOME}/.config/jackett:/config # config files
```

Nothing particular in this configuration, it's pretty similar to other linuxserver.io images.
An interesting setting is the torrent blackhole directory. When you do manual searches, Jackett will put `.torrent` files there, to be grabbed by your torrent client directly (Deluge for instance).

As usual, run with `docker-compose up -d`.

#### Configuration and usage

Jackett web UI is available on port 9117.

![Jacket empty providers list](img/jackett_empty.png)

Configuration is available at the bottom of the page. I chose to disable auto-update (I'll rely on the docker images tags myself), and to set `/downloads` as my blackhole directory.

Click on `Add Indexer` and add any torrent indexer that you like. I added 1337x, cpasbien, RARBG, The Pirate Bay and YGGTorrent (need a user/password).

You can now perform a manual search across multiple torrent indexers in a clean interface with no trillion ads pop-up everywhere. Then choose to save the .torrent file to the configured blackhole directory, ready to be picked up by Deluge automatically !

![Jacket manual search](img/jackett_manual.png)

### Setup NZBGet

#### Docker container

Once again we'll use the Docker image from linuxserver and set it in a docker-compose file.

```yaml
nzbget:
    container_name: nzbget
    image: linuxserver/nzbget:101
    restart: unless-stopped
    network_mode: host
    environment:
      - PUID=1000 # default user id, for downloaded files access rights
      - PGID=1000 # default group id, for downloaded files access rights
      - TZ=Europe/Paris # timezone
    volumes:
      - /media/${USER}/data1/downloads/nzbget:/downloads # download folder
      - ${HOME}/.config/nzbget:/config # config files
```

#### Configuration and usage

After running the container, web UI should be available on `localhost:6789`.
Username: nzbget
Password: tegbzn6789

![NZBGet](img/nzbget_empty.png)

Since NZBGet stays on my local network, I choose to disable passwords (`Settings/Security/ControlPassword` set to empty).

The important thing to configure is the url and credentials of your newsgroups server (`Settings/News-servers`). I have a Frugal Usenet account at the moment, I set it up with TLS encryption enabled.

Default configuration suits me well, but don't hesitate to have a look at the `Paths` configuration.

You can manually add .nzb files to download, but the goal is of course to have Sonarr and Radarr take care of it automatically.

### Setup Plex (optional)

I recommend installing Plex Media Server NOT on the SBC but on a Windows or Macintosh desktop computer you already have running on the same network.  This will help offload some of the processor load of streaming your content from the SBC and free up RAM for other services.

[Download Plex Media Server](https://www.plex.tv/media-server-downloads/)

Additionally, if you have a paid Plex Pass, and a computer with a GPU in it, you can setup Plex to use your very efficient GPU to handle all transcoding needed. [See here for instructions](https://support.plex.tv/articles/115002178853-using-hardware-accelerated-streaming/)   

#### Configuration

Plex Web UI should be available at `localhost:32400` (replace `localhost` with the ip of the computer where it is installed, if needed).
You'll have to login first (registration is free), then Plex will ask you to add your libraries.
I have two libraries:

- Movies
- TV shows

I have 2 mapped network drives (thank you Samba) on my Windows computer where I am running Plex Media Server.  These mapped drives connect to the respective share I have setup on the download/seed box, one for movies and the other for TV shows.  To find the shares on your Windows computer, the SBC Samba docker container can be found by using the UNC of \\odroid (or \\raspberrypi). If you changed the default hostname in Linux, then it will use this name instead. These shares must be mapped prior to using them with Plexon Windows and setting up your libraries. 

After setting up your libraries, Plex will scan your files and gather extra content; it may take some time, but you can watch it happen by logging into the Plex UI.

A few things I like to configure in the Plex settings:

- Tick "Update my library automatically"

You can already watch your stuff through the Web UI. Note that it's also available from a login-secured public URL proxified by Plex servers (see `Settings/Server/Remote Access`), note the access URL or choose to disable public forwarding.

#### Setup Plex clients

Plex clients are available for most devices. I use it on my Android phone, my wife uses it on her Amazon Kindle Fire, we use it on a Chromecast in the bedroom, and an Amazon Fire TV Stick in the Living Room. Nothing particular to configure, just download the app, log into it, enter the validation code and you are done.

On a Linux Desktop, there are several alternatives.
Historically, Plex Home Theater, based on XBMC/Kodi was the principal media player, and by far the client with the most features. It's quite comparable to XBMC/Kodi, but fully integrates with Plex ecosystem. 

Recently, Plex team decided to move towards a completely rewritten player called Plex Media Player. It's not officially available for Linux yet, but can be [built from sources](https://github.com/plexinc/plex-media-player). A user on the forums made [an AppImage for it](https://forums.plex.tv/discussion/278570/plex-media-player-packages-for-linux). Just download and run, it's plug and play. It has a very shiny UI, but lacks some features of PHT. For example: editing subtitles offset.

![Plex Media Player](img/plex_media_player.jpg)

If it does not suit you, there is also now an official [Kodi add-on for Plex](https://www.plex.tv/apps/computer/kodi/). [Download Kodi](http://kodi.wiki/view/HOW-TO:Install_Kodi_for_Linux), then browse add-ons to find Plex.

Also the old good Plex Home Theater is still available, in an open source version called [OpenPHT](https://github.com/RasPlex/OpenPHT).

### Setup Sonarr

#### Docker container

Guess who made a nice Sonarr Docker image? Linuxserver.io !

Let's go:

```yaml
sonarr:
    container_name: sonarr
    image: linuxserver/sonarr:109
    restart: unless-stopped
    network_mode: host
    environment:
      - PUID=1000 # default user id, for downloaded files access rights
      - PGID=1000 # default group id, for downloaded files access rights
      - TZ=Europe/Paris # timezone
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ${HOME}/.config/sonarr:/config # config files
      - /media/${USER}/data1/downloads/complete/Series:/tv # tv shows folder
      - /media/${USER}/data1/downloads/deluge/complete:/downloads # deluge download folder
```

`docker-compose up -d`

Sonarr web UI listens on port 8989 by default. You need to mount your tv shows directory (the one where everything will be nicely sorted and named). And your download folder, because sonarr will look over there for completed downloads, then move them to the appropriate directory.

#### Configuration

Sonarr should be available on `localhost:8989`. Go straight to the `Settings` tab.

![Sonarr settings](img/sonarr_settings.png)

Enable `Ignore Deleted Episodes`: if like me you delete files once you have watched them, this makes sure the episodes won't be re-downloaded again.

In `Media Management`, you can choose to rename episodes automatically. This is a very nice feature I've been using for a long time.

`Indexers` is the important tab: that's where Sonarr will grab information about released episodes. Nowadays a lot of Usenet indexers are relying on Newznab protocol: fill-in the URL and API key you are using. You can find some indexers on this [subreddit wiki](https://www.reddit.com/r/usenet/wiki/indexers). It's nice to use several ones since there are quite volatile. You can find suggestions on Sonarr Newznab presets. Some of these indexers provide free accounts with a limited number of API calls, you'll have to pay to get more. Usenet-crawler is one of the best free indexers out there.

For torrents indexers, I activate Torznab custom indexers that point to my local Jackett service. This allows searches across all torrent indexers configured in Jackett. You have to configure them one by one though.

Get torrent indexers Jackett proxy URLs by clicking `Copy Torznab Feed` in Jackett Web UI. Use the global Jackett API key as authentication.

![Jackett indexers](img/jackett_indexers.png)

![Sonarr torznab add](img/sonarr_torznab.png)

`Download Clients` tab is where we'll configure links with our two download clients: NZBGet and Deluge.
There are existing presets for these 2 that we'll fill with the proper configuration.

NZBGet configuration:
![Sonarr NZBGet configuration](img/sonarr_nzbget.png)

Deluge configuration:
![Sonarr Deluge configuration](img/sonarr_deluge.png)

Enable `Advanced Settings`, and tick `Remove` in the Completed Download Handling section. This tells Sonarr to remove torrents from deluge once processed.

In `Connect` tab, we'll configure Sonarr to send notifications to Plex when a new episode is ready:
![Sonarr Plex configuration](img/sonarr_plex.png)

#### Give it a try

Let's add a serie !

![Adding a serie](img/sonarr_add.png)

Enter the serie name, then you can choose a few things:

- Monitor: what episodes do you want to mark as monitored? All future episodes, all episodes from all seasons, only latest seasons, nothing? Monitored episodes are the episodes Sonarr will download automatically.
- Profile: quality profile of the episodes you want (HD-1080p is the most popular I guess).

You can then either add the serie to the library (monitored episode research will start asynchronously), or add and force the search.

![Season 1 in Sonarr](img/sonarr_season1.png)

Wait a few seconds, then you should see that Sonarr started doing its job. Here it grabed files from my Usenet indexers and sent the download to NZBGet automatically.

![Download in Progress in NZBGet](img/nzbget_download.png)

You can also do a manual search for each episode, or trigger an automatic search.

When download is over, you can head over to Plex and see that the episode appeared correctly, with all metadata and subtitles grabbed automatically. Applause !

![Episode landed in Plex](img/mindhunter_plex.png)

### Setup Radarr

Radarr is a fork of Sonarr, made for movies instead of TV shows. For a good while I've used CouchPotato for that exact purpose, but have not been really happy with the results. Radarr intends to be as good as Sonarr !

#### Docker container

Radarr is *very* similar to Sonarr. You won't be surprised by this configuration.

```yaml
radarr:
    container_name: radarr
    image: linuxserver/radarr:80
    restart: unless-stopped
    network_mode: host
    environment:
      - PUID=1000 # default user id, for downloaded files access rights
      - PGID=1000 # default group id, for downloaded files access rights
      - TZ=Europe/Paris # timezone
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ${HOME}/.config/radarr:/config # config files
      - /media/${USER}/data1/downloads/movies:/movies # movies folder
      - /media/${USER}/data1/downloads/ongoing:/downloads # download folder
```

#### Configuration

Radarr Web UI is available on port 7878.
Let's go straight to the `Settings` section.

I enable `Ignore Deleted Movies` to make sure movies that I delete won't be downloaded again by Radarr. 

As for Sonarr, the `Indexers` section is where you'll configure your torrent and nzb sources.

Nowadays a lot of Usenet indexers are relying on Newznab protocol: fill-in the URL and API key you are using. You can find some indexers on this [subreddit wiki](https://www.reddit.com/r/usenet/wiki/indexers). It's nice to use several ones since there are quite volatile. You can find suggestions on Radarr Newznab presets. Some of these indexers provide free accounts with a limited number of API calls, you'll have to pay to get more. Usenet-crawler is one of the best free indexers out there.
For torrents indexers, I activate Torznab custom indexers that point to my local Jackett service. This allows searches across all torrent indexers configured in Jackett. You have to configure them one by one though.

Get torrent indexers Jackett proxy URLs by clicking `Copy Torznab Feed`. Use the global Jackett API key as authentication.

![Jackett indexers](img/jackett_indexers.png)

![Sonarr torznab add](img/sonarr_torznab.png)

`Download Clients` tab is where we'll configure links with our two download clients: NZBGet and Deluge.
There are existing presets for these 2 that we'll fill with the proper configuration.

NZBGet configuration:
![Sonarr NZBGet configuration](img/sonarr_nzbget.png)

Deluge configuration:
![Sonarr Deluge configuration](img/sonarr_deluge.png)

Enable `Advanced Settings`, and tick `Remove` in the Completed Download Handling section. This tells Radarr to remove torrents from deluge once processed.

In `Connect` tab, we'll configure Radarr to send notifications to Plex when a new episode is ready:
![Sonarr Plex configuration](img/sonarr_plex.png)

#### Give it a try

Let's add a movie !

![Adding a movie in Radarr](img/radarr_add.png)

Enter the movie name, choose the quality you want, and there you go.

You can then either add the movie to the library (monitored movie research will start asynchronously), or add and force the search.

Wait a few seconds, then you should see that Radarr started doing its job. Here it grabed files from my Usenet indexers and sent the download to NZBGet automatically.

You can also do a manual search for each movie, or trigger an automatic search.

When download is over, you can head over to Plex and see that the movie appeared correctly, with all metadata and subtitles grabbed automatically. Applause !

![Movie landed in Plex](img/busan_plex.png)

#### Movie discovering

I like the discovering feature. When clicking on `Add Movies` you can select `Discover New Movies`, then browse through a list of TheMovieDB recommended or popular movies.

![Movie landed in Plex](img/radarr_recommendations.png)

On the rightmost tab, you'll also see that you can setup Lists of movies. What if you could have in there a list of the 250 greatest movies of all time and just one-click download the ones you want?

This can be set up in `Settings/Lists`. I activated the following lists:

- StevenLu: that's an [interesting project](https://github.com/sjlu/popular-movies) that tries to determine by certain heuristics the current popular movies.
- IMDB TOP 250 movies of all times from Radarr Lists presets
- Trakt Lists Trending and Popular movies

I disabled automatic sync for these lists: I want them to show when I add a new movie, but I don't want every item of these lists to be automatically synced with my movie library.

## Manage it all from your mobile

On Android, I'm using [nzb360](http://nzb360.com) to manage NZBGet, Deluge, Sonarr and Radarr.
It's a beautiful and well-thinked app. Easy to get a look at upcoming tv shows releases (eg. "when will the next f**cking Game of Thrones episode be released?").

![NZB360](img/nzb360.png)

The free version does not allow you to add new shows. Consider switching to the paid version (6$) and support the developer.

## Going Further

Some stuff worth looking at that I do not use at the moment:

- [NZBHydra](https://github.com/theotherp/nzbhydra): meta search for NZB indexers (like [Jackett](https://github.com/Jackett/Jackett) does for torrents). Could simplify and centralise nzb indexers configuration at a single place.
- [Organizr](https://github.com/causefx/Organizr): Embed all these services in a single webpage with tab-based navigation
- [Plex sharing features](https://www.plex.tv/features/#feat-modal)
- [Headphones](https://github.com/rembo10/headphones): Automated music download. Like Sonarr but for music albums. I've been using it for a while, but it did not give me satisfying results. I also tend to rely entirely on a Spotify premium account to manage my music collection now.
- [Mylar](https://github.com/evilhero/mylar): like Sonarr, but for comic books.
- [Ombi](http://www.ombi.io/): Web UI to give your shared Plex instance users the ability to request new content
- [PlexPy](https://github.com/JonnyWong16/plexpy): Monitoring interface for Plex. Useful is you share your Plex server to multiple users.
- Radarr lists automated downloads, to fetch best movies automatically. [Rotten Tomatoes certified movies](https://www.rottentomatoes.com/browse/cf-in-theaters/) would be a nice list to parse and get automatically.
