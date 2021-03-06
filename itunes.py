"""
    Custom Http handler
    Author: Pascal Noisette

"""
import datetime
import hashlib
import urllib
import os

import PyRSS2Gen
from tinytag import TinyTag


class ItunesRSS2(PyRSS2Gen.RSS2):
    def __init__(self, base_url, path, items):
        """
        Override PyRSS2Gen.RSS2 constructor
        - to simplify constructor args for user
        - to have custom namespaces
        """
        super().__init__(
            title=path,
            link=path,
            lastBuildDate=datetime.datetime.now(),
            items=items,
            description="",
            image=PyRSS2Gen.Image(base_url + "/feedIcon.png", path, path)
        )

        self.base_url=base_url
        self.rss_attrs["xmlns:itunes"] = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        self.rss_attrs["xmlns:atom"] = "http://www.w3.org/2005/Atom"
        self.rss_attrs["xmlns:media"] = "http://search.yahoo.com/mrss/"
        self.rss_attrs["xmlns:dcterms"] = "http://purl.org/dc/terms/"

    def publish(self, handler):
        """
        Override PyRSS2Gen.RSS2.publish to add stylesheet to header
        """
        handler.processingInstruction("xml-stylesheet" ,'type="text/xsl" href="'+self.base_url+'/style.xsl"');
        handler.characters("\n");
        super().publish(handler)


class ItunesRSSItem(PyRSS2Gen.RSSItem):
    def __init__(self, base_url, rel_file, full_name):
        """
        Override PyRSS2Gen.RSSItem constructor to simplify constructor args for user
        """
        tag = TinyTag.get(rel_file)
        if tag.title is None:
            tag.title, ext = os.path.splitext(os.path.basename(rel_file))
        super().__init__(
            title=tag.title,
            link=urllib.parse.quote(rel_file),
            author=tag.artist,
            enclosure=PyRSS2Gen.Enclosure(base_url + "/" + urllib.parse.quote(rel_file), tag.filesize, "audio/mpeg"),
            guid=PyRSS2Gen.Guid(hashlib.sha256(full_name.encode('utf-8')).hexdigest(), isPermaLink=False),
            pubDate=tag.year
        )

    def publish_extensions(self, handler):
        """
         Override to set values of various itunes xmlns tags
         """
        if self.enclosure.url.endswith(".mp3"):
            PyRSS2Gen._element(handler, "image", PyRSS2Gen.Image(self.enclosure.url + ".png", self.title, self.link))


def is_valid_itunes_rss_item(rel_file):
    """
    Hide TinyTag from user, supply him a predicate
    """
    return TinyTag.is_supported(rel_file)

