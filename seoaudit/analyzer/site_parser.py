# -*- coding: utf-8 -*-
"""
This module contains SiteParser class which defines a parser at website level (list of urls).

Typical usage example:

    site_parser = SiteParser(url, LXMLPageParser(url), urls=None, parse_sitemap_urls=True)
    while site_parser.parse_next_page():
        print("Running checks for url: {}".format(site_parser.get_current_url()))
        # do something

Todo:
    * check site for broken links

"""

import lxml.etree
import requests
import urllib.robotparser
import urllib.parse

from seoaudit.analyzer.page_parser import AbstractPageParser, LXMLPageParser


class SiteParser(object):
    """ Website level parser, uses a page parser object as the core of it's parsing functionalities with the urls
    list being predefined or crawled from the sitemap file. """

    def __init__(self, base_url, page_parser: AbstractPageParser = None, urls=None, sitemap_link=None,
                 parse_sitemap_urls=False):
        """

        Args:
            base_url:
            page_parser:
            urls:
            parse_sitemap_urls:

        """

        # if urls list is not defined initialize list with base_url
        if urls is None:
            self.urls = [base_url]
        else:
            self.urls = urls

        self.current_page_index = 0

        # if page parser is not defined default to LXMLPageParser
        if page_parser is None:
            self.page_parser = LXMLPageParser(base_url)
        else:
            self.page_parser = page_parser

        self.base_url = base_url

        self.sitemap_urls = []

        # crawl sitemap referenced by head link[@rel='sitemap'] metadata of base url
        if sitemap_link is None:
            sitemap_link = self.page_parser.get_elements("(/html/head/link[@rel='sitemap'])/@href")
            sitemap_link = sitemap_link[0] if len(sitemap_link) >= 1 else None

        if sitemap_link is not None:
            r = requests.get(urllib.parse.urljoin(self.base_url, sitemap_link))
            try:
                self.sitemap = lxml.etree.fromstring(r.content)

                if parse_sitemap_urls:
                    for sitemap_el in self.sitemap:
                        self.urls.append(sitemap_el[0].text)
                        self.sitemap_urls.append(sitemap_el[0].text)

            except lxml.etree.XMLSyntaxError:
                print("xml error")
                self.sitemap = None

        # crawl robots.txt file found in base_url + "/robots.txt"
        self.robort_parser = urllib.robotparser.RobotFileParser()
        self.robort_parser.set_url(base_url + "/robots.txt")
        self.robort_parser.read()

        if self.robort_parser.entries == 0:
            self.robort_parser = None

        # crawl web app manifest file referenced by head link[@rel='manifest'] metadata of base url
        manifest_link = self.page_parser.get_elements("(/html/head/link[@rel='manifest'])/@href")
        manifest_link = manifest_link[0] if len(manifest_link) >= 1 else None

        if manifest_link is not None:
            self.web_app_manifest = requests.get(urllib.parse.urljoin(self.base_url, manifest_link))
            self.web_app_manifest = self.web_app_manifest.json()

        manifest_link = self.page_parser.get_elements("(/html/head/link[@rel='manifest'])/@href")
        manifest_link = manifest_link[0] if len(manifest_link) >= 1 else None

        if manifest_link is not None:
            self.web_app_manifest = requests.get(urllib.parse.urljoin(self.base_url, manifest_link))
            self.web_app_manifest = self.web_app_manifest.json()

        # crawl browser config file referenced by head link[@rel='msapplication-config'] metadata of base url
        browserconfig_link = self.page_parser.get_elements("(/html/head/meta[@name='msapplication-config'])/@content")
        browserconfig_link = browserconfig_link[0] if len(browserconfig_link) >= 1 else None

        if browserconfig_link is not None:
            r = requests.get(urllib.parse.urljoin(self.base_url, browserconfig_link))
            try:
                self.browserconfig = lxml.etree.fromstring(r.content)

            except lxml.etree.XMLSyntaxError:
                self.browserconfig = None

        # sites cache is used in site checks (e.g. Site_Check.TITLE_REPETITION)
        self.sites_cache = []

    def parse_next_page(self, ):
        """
        Parse next page using page parser object.

        Returns:
            boolean : True if next page was parse, False if end of list of urls was reached

        """

        self.current_page_index += 1

        if self.current_page_index >= len(self.urls):
            # end of urls list reached
            return False
        self.page_parser = LXMLPageParser(self.urls[self.current_page_index])

        # add to site cache for SiteCheck-s
        self.sites_cache.append(
            {"url": self.page_parser.url, "content": self.page_parser.text, "title": self.page_parser.title,
             "description": self.page_parser.description})

        return True

    def get_current_url(self):
        """

        Returns:
            str : url of currently indexed page

         """
        return self.urls[self.current_page_index]
