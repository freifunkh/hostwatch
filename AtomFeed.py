#!/usr/bin/python3

import datetime
import xml.etree.ElementTree as ET

class AtomFeed():
    def __init__( self, filePath=None, maxEntries=2, title=None, author=None, link=None ):
        ET.register_namespace( '', 'http://www.w3.org/2005/Atom' )
        self.maxEntries = maxEntries
        self.root = None
        self.ns = {'atom': 'http://www.w3.org/2005/Atom'}
        if filePath:
            tree = ET.parse( filePath )
            self.root = tree.getroot()
        elif title and author and link:
            self.root = ET.fromstring( '<?xml version="1.0"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>' + title + '</title><author><name>' + author + '</name></author><updated>2000–01–01T00:00:00Z</updated><link rel="alternate" href="' + link + '"/><entry><title>dummy entry</title><summary></summary><updated>2000–01–01T00:00:00Z</updated><id>dummyid</id></entry></feed>' )
        else:
            raise ValueError


    def GetLink( self ):
        link = None
        try:
            link = self.root.find( 'atom:link', self.ns ).text
        except:
            pass
        if link and not link.endswith('/'):
            link += '/'
        return link if link else ''


    def WriteFile( self, filePath ):
        # delete old entries
        id_list = []
        for entry in self.root.findall( 'atom:entry', self.ns ):
            id_list.append( entry.find( 'atom:id', self.ns ).text )
        id_list.sort()
        del id_list[ (self.maxEntries*-1): ]

        for entry in self.root.findall( 'atom:entry', self.ns ):
            if entry.find( 'atom:id', self.ns ).text in id_list:
                self.root.remove( entry )

        now = datetime.datetime.utcnow()
        updated = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        updated_tag = self.root.find( 'atom:updated', self.ns )
        updated_tag.text = updated

        with open( filePath, 'w' ) as f:
            f.write( ET.tostring( self.root, encoding="utf-8" ).decode() )


    def AddEntry( self, title, summary ):
        now = datetime.datetime.utcnow()

        ne = ET.SubElement( self.root, 'entry' )

        ne_title = ET.SubElement( ne, 'title' )
        ne_title.text = title

        ne_summary = ET.SubElement( ne, 'summary' )
        ne_summary.text = summary

        ne_updated = ET.SubElement( ne, 'updated' )
        ne_updated.text = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        ne_id = ET.SubElement( ne, 'id' )
        ne_id.text = self.GetLink() + now.strftime("%Y%m%d%H%M%S")
