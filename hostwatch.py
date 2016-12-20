#!/usr/bin/python3

import configparser
import datetime
import json
import os
import os.path
import subprocess
import xml.etree.ElementTree as ET

import AtomFeed

def Ping( address ):
    online = False
    try:
        r = subprocess.run( ["ping",  "-W", "1", "-c", "1", address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        online = ( r.returncode == 0 )
    except:
        pass

    if not online:
        try:
            r = subprocess.run( ["ping6", "-W", "1", "-c", "1", address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
            online = ( r.returncode == 0 )
        except:
            pass

    return online


def PingAll( hosts_config, feedFolder, url ):
    feed_file = feedFolder + '_all.atom'
    feed = None
    if os.path.exists( feed_file ):
        feed = AtomFeed.AtomFeed( filePath=feed_file, maxEntries=100 )
    else:
        feed = AtomFeed.AtomFeed( title='hostwatch: all', author='hostwatch', link=url, maxEntries=100 )

    for host in hosts:
        new_status = Ping( host['address'] )
        if new_status != host['online']:
            host['lastchange'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            host['online'] = new_status
            UpdateLocalFeed( host['name'], host['online'], feedFolder, url )
            title = ( 'Online' if new_status else 'Offline' ) + ': ' + host['name']
            summary = '"' + host['name'] + '" ist jetzt ' + ( 'online' if new_status else 'offline' ) + '.'
            feed.AddEntry( title=title, summary=summary )
    feed.WriteFile( feed_file )


def UpdateLocalFeed( name, online, feedFolder, url ):
    feed_file = feedFolder + name + '.atom'
    url = url + feed_file + '/'

    feed = None
    if os.path.exists( feed_file ):
        feed = AtomFeed.AtomFeed( filePath=feed_file )
    else:
        feed = AtomFeed.AtomFeed( title='hostwatch: ' + name, author='hostwatch', link=url )

    title = 'online' if online else 'offline'
    summary = '"' + name + '" ist jetzt ' + title + '!'

    feed.AddEntry( title=title, summary=summary )
    feed.WriteFile( feed_file )


def ReadHosts( hostsJSON ):
    hosts = None
    if os.path.exists( hostsJSON ):
        with open( hostsJSON, 'r' ) as f:
            hosts = json.load( f )
    else:
        hosts = json.loads( '[{"lastchange": "2000-01-01T00:00:00Z", "online": false, "name": "localhost", "address": "127.0.0.1"}]' )
    return hosts


def WriteHosts( hosts, hostsJSON ):
    with open( hostsJSON, 'w' ) as f:
        json.dump( hosts, f )


if __name__ == "__main__":
    config_path = os.path.dirname( __file__ ) + '/hostwatch.ini'
    config = configparser.ConfigParser()
    config.read( config_path )
    hosts = ReadHosts( config['general']['HostsJSON'] )
    PingAll( hosts, config['general']['FeedFolder'], config['general']['URL'] )
    WriteHosts( hosts, config['general']['HostsJSON'] )
