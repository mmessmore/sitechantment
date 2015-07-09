__author__ = 'Michael Messmore'
__email__ = 'mike@messmore.org'
__version__ = '0.1.0'

import sys
import os
import re
from urlparse import urljoin, urlparse

import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import HTMLChunker
import requests
from bs4 import BeautifulSoup


class SiteCheck():

    checked = []
    bad_words = []
    htmlcomments = re.compile('\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>')

    def __init__(self, lang="en_US", client=requests, verbosity=0,
                 dictfile=""):
        self.lang = lang
        self.client = requests
        self.verbosity = verbosity
        self.dictfile = dictfile

        self.dic = enchant.Dict(lang)
        if os.path.isfile(self.dictfile):
            with open(self.dictfile) as f:
                for line in f:
                    self.dic.add_to_session(line.strip())
        self.sc = SpellChecker(self.dic, chunkers=(HTMLChunker,))

    def verbose(self, msg, level=0):
        if level >= self.verbosity:
            print msg

    def glean_links(self, url, text):
        soup = BeautifulSoup(text, 'html.parser')
        old_res = urlparse(url)
        links = []
        for anchor in soup.find_all('a'):
            new_url = urljoin(url, anchor.get('href'))
            new_res = urlparse(new_url)
            if new_res.netloc == old_res.netloc:
                links.append(new_url)
        return links

    def check(self, url):
        if url in self.checked:
            return False

        res = requests.get(url)
        # strip html comments before we go nuts
        self.sc.set_text(self.htmlcomments.sub('', res.text))
        for err in self.sc:
            self.verbose("ERROR: "+ err.word, 1)
            if err.word not in self.bad_words:
                self.bad_words.append(err.word)
        self.checked.append(url)

        for link in self.glean_links(url, res.text):
            self.check(url)
        return self.bad_words

    def update_pwl(self):
        if self.dictfile == "":
            return False
        df = open(self.dictfile, 'a')
        for word in set(self.bad_words):
            verbose("Adding {0} to dictionary: {1}".format(word,
                                                           self.dictfile), 1)
            df.write(word + "\n")
