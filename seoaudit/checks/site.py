# -*- coding: utf-8 -*-
""" This modules contains all of the predefined site checks. Site check works at a website level (list of urls).

Predefined site checks are enumerated in SiteCheck enum with each enum value containing the name of the class
that implements the defined check by extending AbstractSiteCheck class.

When functionality of predefined site checks is not enough, custom SiteCheck can be created by extending
AbstractSiteCheck class.

Typical usage example:

    url = "https://google.com"
    site_parser = SiteParser(url, LXMLPageParser(url), urls=None, parse_sitemap_urls=True)
    check = check_site(SiteCheck.SITEMAP_FOUND, site_parser)


Todo:
    * icons and theme metadata check (check icon files, manifest file, browser-config file) (fileimage size)
    * content repetition check by top keywords

"""

from enum import Enum
import abc
from collections import defaultdict

from seoaudit.analyzer.site_parser import SiteParser


class AbstractSiteCheck(metaclass=abc.ABCMeta):
    """ Abstract class to be extended in element site classes. """

    @abc.abstractmethod
    def check_site(self, parser: SiteParser, **kwargs):
        """ Returns check validity of the given site

        Args:
            parser (SiteParser): website parser object
            *kwargs: keyword check arguments

        Returns: a boolean value representing checks validity
        """


class SitemapFoundCheck(AbstractSiteCheck):
    """ Checks if site sitemap is found. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        return parser.sitemap is not None


class RobotsFoundCheck(AbstractSiteCheck):
    """ Checks if site robots file is found. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        return parser.robort_parser is not None


class ManifestFoundCheck(AbstractSiteCheck):
    """ Checks if site web app manifest file is found. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        return parser.web_app_manifest is not None


class BrowserConfigFoundCheck(AbstractSiteCheck):
    """ Checks if site browser config file is found. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        return parser.browserconfig is not None


class PageCrawlableCheck(AbstractSiteCheck):
    """ Checks if page is crawlable by site's robots settings. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        can_fetch = parser.robort_parser.can_fetch("*", parser.page_parser.url)

        # if robots meta tag is found check it too
        elements = parser.page_parser.get_elements("(/html/head/meta[@name='robots'])")
        if len(elements) >= 1:
            element = elements[0]
            content = parser.page_parser.get_element_attribute(element, "content")
            can_fetch &= ("noindex" not in content and "none" not in content)

        return can_fetch


class PageInSitemapCheck(AbstractSiteCheck):
    """ Checks if page's url is found in site's sitemap. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        return not all(
            [(sitemap_url != parser.page_parser.url) and (sitemap_url != parser.page_parser.url + "/") for sitemap_url
             in parser.sitemap_urls])


class TitleRepetitionCheck(AbstractSiteCheck):
    """ Checks if title metadata repetition across different pages. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        titles_list = [d['title'] for d in parser.sites_cache]
        url_list = [d['url'] for d in parser.sites_cache]

        titles_dict = defaultdict(list)
        for i, item in enumerate(titles_list):
            titles_dict[item].append(i)
        titles_dict = {k: [url_list[v] for v in v] for k, v in titles_dict.items() if len(v) > 1}
        if len(titles_dict) > 0:
            return False, titles_dict

        return True


class DescriptionRepetitionCheck(AbstractSiteCheck):
    """ Checks if description metadata repetition across different pages. """

    def check_site(self, parser: SiteParser, **unused):
        """
        Args:
            parser (SiteParser): website parser object
            unused: unused parameter defined to extend AbstractSiteCheck
        Returns:
            a boolean value representing checks validity

        """
        descriptions_list = [d['description'] for d in parser.sites_cache]
        url_list = [d['url'] for d in parser.sites_cache]

        descriptions_dict = defaultdict(list)
        for i, item in enumerate(descriptions_list):
            descriptions_dict[item].append(i)
        descriptions_dict = {k: [url_list[v] for v in v] for k, v in descriptions_dict.items() if len(v) > 1}
        if len(descriptions_dict) > 0:
            return False, descriptions_dict

        return True


class SiteCheck(Enum):
    SITEMAP_FOUND = SitemapFoundCheck
    ROBOTS_FOUND = RobotsFoundCheck
    PAGE_CRAWLABLE = PageCrawlableCheck
    PAGE_IN_SITEMAP = PageInSitemapCheck
    MANIFEST_FOUND = ManifestFoundCheck
    BROWSERCONFIG_FOUND = BrowserConfigFoundCheck
    TITLE_REPETITION = TitleRepetitionCheck
    DESCRIPTION_REPETITION = DescriptionRepetitionCheck


def check_site(check: SiteCheck, parser: SiteParser, **kwargs):
    return check.value().check_site(parser, **kwargs)
