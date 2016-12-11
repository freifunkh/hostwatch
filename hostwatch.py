#!/usr/bin/python3

import datetime
import json
import os
import os.path
import subprocess
import xml.etree.ElementTree as ET

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

    ET.register_namespace( '', 'http://www.w3.org/2005/Atom' )
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    root = None
    if os.path.exists( feed_file ):
        tree = ET.parse( feed_file )
        root = tree.getroot()
    else:
        root = ET.fromstring( '<?xml version="1.0"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>hostwatch: ' + name + '</title><author><name>hostwatch</name></author><updated>2000–01–01T00:00:00Z</updated><link rel="alternate" href="http://127.0.0.1/hostwatch"/></feed>' )

    # delete old entries
    id_list = []
    for entry in root.findall( 'atom:entry', ns ):
        id_list.append( entry.find( 'atom:id', ns ).text )
    id_list.sort()
    del id_list[-2:]

    for entry in root.findall( 'atom:entry', ns ):
        if entry.find( 'atom:id', ns ).text in id_list:
            root.remove( entry )

    now = datetime.datetime.utcnow()
    updated = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    entry_id = now.strftime("%Y%m%d%H%M%S")
    updated_tag = root.find( 'atom:updated', ns )
    updated_tag.text = updated

    ne = ET.SubElement( root, 'entry' )

    ne_title = ET.SubElement( ne, 'title' )
    if online:
        ne_title.text = 'online'
    else:
        ne_title.text = 'offline'

    ne_summary = ET.SubElement( ne, 'summary' )
    ne_summary.text = '"' + name + '" ist jetzt ' + ne_title.text + '!'

    ne_updated = ET.SubElement( ne, 'updated' )
    ne_updated.text = updated

    ne_id = ET.SubElement( ne, 'id' )
    ne_id.text = url + entry_id
    
    with open( feed_file, 'w' ) as f:
        f.write( ET.tostring( root, encoding="utf-8" ).decode() )


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
