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
    try:
        r = subprocess.run( ["ping6", "-W", "1", "-c", "1", address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        return ( r.returncode == 0 )
    except:
        return False


def PingAll( hosts ):
    feed_file = gFeedFolder + '_all.atom'
    feed = None
    if os.path.exists( feed_file ):
        feed = AtomFeed.AtomFeed( filePath=feed_file, maxEntries=100 )
    else:
        feed = AtomFeed.AtomFeed( title='hostwatch: all', author='hostwatch', link='htto://moridius.ffh', maxEntries=100 )

    for host in hosts:
        new_status = Ping( host['address'] )
        if new_status != host['online']:
            host['lastchange'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            host['online'] = new_status
            UpdateLocalFeed( host['name'], host['online'] )
            title = ( 'Online' if new_status else 'Offline' ) + ': ' + host['name']
            summary = '"' + host['name'] + '" ist jetzt ' + ( 'online' if new_status else 'offline' ) + '.'
            feed.AddEntry( title=title, summary=summary )
    feed.WriteFile( feed_file )


def UpdateLocalFeed( name, online ):
    feed_file = gFeedFolder + name + '.atom'
    url = gURL + feed_file + '/'

    feed = None
    if os.path.exists( feed_file ):
        feed = AtomFeed.AtomFeed( filePath=feed_file )
    else:
        feed = AtomFeed.AtomFeed( title='hostwatch: ' + name, author='hostwatch', link='htto://moridius.ffh' )

    title = 'online' if online else 'offline'
    summary = '"' + name + '" ist jetzt ' + title + '!'

    feed.AddEntry( title=title, summary=summary )
    feed.WriteFile( feed_file )


def ReadHosts():
    hosts = None
    if os.path.exists( gHostsJSON ):
        with open( gHostsJSON, 'r' ) as f:
            hosts = json.load( f )
    else:
        hosts = json.loads( '[{"lastchange": "2000-01-01T00:00:00Z", "online": false, "name": "localhost", "address": "127.0.0.1"}]' )
    return hosts


def WriteHosts( hosts ):
    with open( gHostsJSON, 'w' ) as f:
        json.dump( hosts, f )


if __name__ == "__main__":
    hosts = ReadHosts()
    PingAll( hosts )
    WriteHosts( hosts )
