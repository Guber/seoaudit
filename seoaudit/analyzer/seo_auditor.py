# -*- coding: utf-8 -*-
"""
This module contains SeoAuditer class which uses SiteParser and a list of Element, Page and Site checks to identify
SEO errors in a given set of websites.

Typical usage example:

    site_parser = SiteParser(url, LXMLPageParser(url), urls=None, parse_sitemap_urls=True)
    auditer = SEOAuditer(url, site_parser, page_tests, element_tests)
    auditer.run_tests_for_site()


Todo:
    * SEOAuditor initialization with list of urls
    * CLI support and outside config file support (https://martin-thoma.com/configuration-files-in-python/)
    * tests :)
    * output results as html
"""

import json
import time

from seoaudit.checks.element import ElementCheck, AbstractElementCheck, check_content
from seoaudit.checks.site import SiteCheck, check_site
from seoaudit.checks.page import PageCheck, check_page
from seoaudit.analyzer import SiteParser, SeleniumPageParser, LXMLPageParser


class SEOAuditor(object):
    """ Takes a list of urls and runs element, page and site checks on them. Output is returned in JSON format."""

    def __init__(self, url, site_parser: SiteParser, page_checks, element_checks):
        self.__url = url
        self.__site_parser = site_parser
        self.__results = {}
        self.__checks = {"page_checks": page_checks, "element_checks": element_checks}
        self.result_filename = 'seo_audit_' + str(time.time()) + '.json'

    def run_check(self, check, kwargs=None):
        """
        Runs page or site check and appends it's return value to results list.

        Args:
            check: check definition
            kwargs: check keyword arguments
        """
        kwargs = {} if kwargs is None else kwargs

        if isinstance(check, SiteCheck):
            self.append_result(check_site(check, self.__site_parser, **kwargs), check.name, self.__url, str(kwargs))
        elif isinstance(check, PageCheck):
            self.append_result(check_page(check, self.__site_parser.page_parser, **kwargs), check.name, self.__url,
                               str(kwargs))
        # Todo: transfer eun_elements_check logic here
        elif isinstance(check, ElementCheck):
            check_function = check_content
        else:
            raise ValueError("check must be of type SiteCheck, PageCheck or ElementCheck.")

    def run_elements_check(self, query, content_attribute='textContent', checks=()):
        """
        Runs element check and appends it's return value to results list.

        Args:
            query: element xpath query
            content_attribute: element's attribute name
            checks: element check

        """
        elements = self.__site_parser.page_parser.get_elements(query)

        if len(elements) == 0:
            self.append_result(False, "ELEMENT_FOUND", query, None)
            return

        for element in elements:
            content = self.__site_parser.page_parser.get_element_attribute(element, content_attribute)
            element_str = self.__site_parser.page_parser.get_element_code(element)
            element_str = (element_str[:150] + '..') if len(element_str) > 150 else element_str

            if content is None or len(content) == 0:
                self.append_result(False, "ATTRIBUTE_FOUND", element_str, [content_attribute])
                continue

            self.append_result(True, "ATTRIBUTE_FOUND", element_str, [content_attribute])

            for check in checks:
                if issubclass(check[0].value, AbstractElementCheck):
                    self.append_result(check_content(check[0], content, **check[1]), check[0].name, element_str,
                                       check[1])

    def append_result(self, result, check, audited_object="", *kwargs):
        """
        Appends check's result into the results list.

        Args:
            result: check's result
            check: check enum definition
            audited_object: object audited by the check
            kwargs: check's keyword arguments

        """
        if self.__site_parser.get_current_url() not in self.__results.keys():
            self.__results[self.__site_parser.get_current_url()] = []

        self.__results[self.__site_parser.get_current_url()].append(
            {"result": result, "check": check, "check_arguments": kwargs,
             "audited_object": audited_object})

    def get_results(self):
        """ Get results list. """
        return self.__results

    def clear_results(self):
        """ Clear results dict. """
        self.__results = {}

    def run_checks_for_current_page(self):
        """ Runs predefined page and element checks. """

        for test in self.__checks["page_checks"]:
            self.run_check(*test)

        for test in self.__checks["element_checks"]:
            self.run_elements_check(*test)

    def run_checks_for_site(self):
        """ Runs predefined site checks. """

        print("Running checks for url: {}".format(self.__site_parser.get_current_url()))
        self.run_checks_for_current_page()

        with open(self.result_filename, 'w') as fp:
            fp.seek(0)
            json.dump(self.__results, fp, indent=4)

            while self.__site_parser.parse_next_page():
                print("Running checks for url: {}".format(self.__site_parser.get_current_url()))
                self.run_checks_for_current_page()
                fp.seek(0)
                json.dump(self.__results, fp, indent=4)


def main():
    # from nltk.corpus import stopwords
    # stop_words = stopwords.words('english')
    #
    # from nltk.stem.porter import PorterStemmer
    # stemmer = PorterStemmer()

    page_tests = [
        (PageCheck.TEXT_TO_CODE_RATIO, {"min_ratio": 0.1}),
        (PageCheck.DOM_SIZE, {"max_size": 1500}),
        [PageCheck.ELEMENTS_SIMILARITY,
         {"el1_query": "/*", "el2_query": "/html/head/title", "match_most_common": 5}],
        [PageCheck.ELEMENTS_SIMILARITY,
         {"el1_query": "/*", "el2_query": "/html/head/meta[@name='description']/@content", "match_most_common": 5}],
        [PageCheck.ELEMENTS_SIMILARITY,
         {"el1_query": "//h1", "el2_query": "/html/head/meta[@name='description']/@content", "match_most_common": 5}],
        [PageCheck.ELEMENTS_COUNT, {"query": "(//h2)", "min_count": 2}],
        [PageCheck.STRUCTURED_DATA_FOUND, {"type": "json-ld", "property": "@type", "value": "Organization"}],
        [SiteCheck.TITLE_REPETITION],
        [SiteCheck.DESCRIPTION_REPETITION],
        [SiteCheck.PAGE_IN_SITEMAP],
        [SiteCheck.PAGE_CRAWLABLE],
    ]

    # Todo: add regex check for charset = utf-8
    # Todo: add regex check for robots not block page
    element_tests = [
        ("/html", 'lang'),
        ("(/html/head/meta[@charset])", 'charset'),
        ("/html/head/title", 'textContent',
         [(ElementCheck.MIN_LENGTH, {"min_length": 50}),
          (ElementCheck.MAX_LENGTH, {"max_length": 50})]),
        ("(/html/head/meta[@name='description'])", 'content',
         [(ElementCheck.MIN_LENGTH, {"min_length": 50}), (ElementCheck.MAX_LENGTH, {"max_length": 160})]),
        ("(/html/head/meta[@name='viewport'])", 'content'),
        ("(//img)", 'alt'),
        ("(//a[@href])", 'title'),
        ("(/html/head/meta[@name='og:locale'])", 'content'),
        ("(/html/head/meta[@name='og:title'])", 'content'),
        ("(/html/head/meta[@name='og:description'])", 'content'),
        ("(/html/head/meta[@name='og:type'])", 'content'),
        ("(/html/head/meta[@name='og:url'])", 'content'),
        ("(/html/head/meta[@name='og:image'])", 'content'),
        ("(/html/head/meta[@name='twitter:title'])", 'content'),
        ("(/html/head/meta[@name='twitter:description'])", 'content'),
        ("(/html/head/meta[@name='twitter:image'])", 'content'),
        ("(/html/head/meta[@name='twitter:card'])", 'content'),
        ("(/html/head/link[@rel='canonical'])", 'href')
    ]

    url = 'https://green-light.agency'
    # site_parser = SiteParser(url,  SeleniumPageParser(url))
    site_parser = SiteParser(url, LXMLPageParser(url), urls=None, parse_sitemap_urls=True)

    # initiate auditer object
    auditer = SEOAuditor(url, site_parser, page_tests, element_tests)
    auditer.run_checks_for_site()


if __name__ == "__main__":
    main()
