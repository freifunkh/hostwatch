#!/usr/bin/python3

import datetime
import json
import os
import os.path
import subprocess
import xml.etree.ElementTree as ET

import AtomFeed

### Settings in code... 'cause I'm lazy. ###
gHostsJSON = '/home/moridius/scripts/hostwatch/hosts.json'
gFeedFolder = '/home/moridius/scripts/hostwatch/feeds/'
gURL = 'http://127.0.0.1/hostwatch/'
############################################


def Ping( address ):
    r = subprocess.run( ["ping", "-W", "1", "-c", "1", address], stdout=subprocess.DEVNULL )
    return ( r.returncode == 0 )


def PingAll( hosts ):
    for host in hosts:
        if host['name'] == "carter":
            continue # debugging
        #new_status = not host['online']
        new_status = Ping( host['address'] )
        if new_status == True:
            host['lastseen'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        if new_status != host['online']:
            host['online'] = new_status
            UpdateFeed( host['name'], host['online'] )


def UpdateFeed( name, online ):
    feed_file = gFeedFolder + name + '.atom'
    url = gURL + feed_file + '/'

    feed = None
    if os.path.exists( feed_file ):
        feed = AtomFeed( filePath=feed_file )
    else:
        feed = AtomFeed( title='hostwatch: ' + name, author='hostwatch', link='htto://moridius.ffh' )

    title = 'offline'
    if online:
        title = 'online'
    summary = '"' + name + '" ist jetzt ' + ne_title.text + '!'

    feed.AddEntry( title=title, summary=summary )

    feed.WriteFile( feed_file )


def ReadHosts():
    hosts = None
    if os.path.exists( gHostsJSON ):
        with open( gHostsJSON, 'r' ) as f:
            hosts = json.load( f )
    else:
        hosts = json.loads( '[{"lastseen": "2000-01-01T00:00:00Z", "online": false, "name": "localhost", "address": "127.0.0.1"}]' )
    return hosts


def WriteHosts( hosts ):
    with open( gHostsJSON, 'w' ) as f:
        json.dump( hosts, f )


if __name__ == "__main__":
    hosts = ReadHosts()
    PingAll( hosts )
    WriteHosts( hosts )
