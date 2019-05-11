"""
    Custom Http handler
    Author: Pascal Noisette

"""

import os
import fcntl
import io
import optparse
import sys

from itunes import ItunesRSS2, ItunesRSSItem, isValidItunesRSSItem


def get_items(root_dir, base_url):
    for dir_, _, files in os.walk(root_dir):
        for file_name in files:
            rel_dir = os.path.relpath(dir_, os.getcwd())
            rel_file = os.path.join(rel_dir, file_name)
            full_name = os.path.join(dir_, file_name)
            if os.path.isfile(rel_file) and isValidItunesRSSItem(rel_file):
                yield ItunesRSSItem(base_url, rel_file, full_name)


def run(path, file, base_url):
    encoding = sys.getfilesystemencoding()
    f = io.open(file, "w")
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    ItunesRSS2(base_url, path, get_items(path, base_url)).write_xml(f, encoding)
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", help="Output xml file", default="/app/static/index.xml")
    parser.add_option("-d", "--dir", help="Root dir", default="/pub/")
    parser.add_option("-p", "--path", help="Path to parse", default="/pub/")
    parser.add_option("-b", "--base_url", help="Url as prefix", default="http://127.0.0.1:5000/")
    (option, args) = parser.parse_args()
    os.chdir(option.dir)
    run(option.path, option.file, option.base_url)
