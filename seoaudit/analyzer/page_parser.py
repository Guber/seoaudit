# -*- coding: utf-8 -*-
"""
This module contains page parses classes which define page parser objects at single web page level (single url).

Typical usage example:

    page_parser = PageParser(url)
    sitemap_links = page_parser.get_elements("(/html/head/link[@rel='sitemap'])/@href")
    sitemap_link = sitemap_link[0] if len(sitemap_links) >= 1 else None

"""

import abc
from w3lib.html import get_base_url

from selenium.webdriver.remote.webdriver import WebElement
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException

import requests
import lxml.html
import lxml.etree


class AbstractPageParser(metaclass=abc.ABCMeta):
    """ Abstract web page parser. Used as a blueprint for page parser implementations. """

    @abc.abstractmethod
    def __init__(self, url):
        """

        Args:
             url (str): url of the web page to be parsed
        """
        self.url = url

    @abc.abstractmethod
    def get_elements(self, xpath_query: str):
        """
        Get a list of HTML elements using xpath query on page parsed web page.

        Args:
            xpath_query (str): xpath elements query

        Returns:
            list of HTML elements that can be used in other parser methods
        """
        pass

    @abc.abstractmethod
    def get_element_code(self, element) -> str:
        """
        Given an HTML element return its HTML code.

        Args:
            element: HTML element

        Returns:
            string HTML code
        """
        pass

    @abc.abstractmethod
    def get_element_text(self, element) -> str:
        """
        Given an HTML element return its text content.

        Args:
            element: HTML element

        Returns:
            string text content
        """
        pass

    @abc.abstractmethod
    def get_element_attribute(self, element, attribute="textContent") -> str or None:
        """
        Given an HTML element and its attribute name, return attributes content.

        Args:
            element: HTML element
            attribute: attribute name, defaults to textContent

        Returns:
            HTML element's attribute text value
        """
        pass


class SeleniumPageParser(AbstractPageParser):
    """ Web page parser with Selenium Webdriver core.

     Todo:
        * parametrize concrete driver implementation (e.g. Chrome, Firefox) - currently defaults to Chrome
     """

    def __init__(self, url):
        super().__init__(url)

        options = selenium.webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.add_argument("--headless")

        self.__driver = selenium.webdriver.Chrome(chrome_options=options)
        self.__driver.get(url)

        self.text = self.get_element_text(self.get_elements("/*")[0])
        self.base_url = get_base_url(self.text, url)
        self.source = " ".join(self.__driver.page_source.split())
        self.title = self.__driver.title

        description_el = self.get_elements("(/html/head/meta[@name='description'])")
        description_el = description_el[0] if len(description_el) >= 1 else None
        self.description = self.get_element_attribute(description_el, "content")

    def get_elements(self, xpath_query: str):
        """
        Get a list of HTML elements using xpath query on page parsed web page.

        Args:
            xpath_query (str): xpath elements query

        Returns: a list of selenium Webdriver elements
        """
        if "/@" in xpath_query:
            query_attribute = xpath_query.split("/@")[1]
            xpath_query = xpath_query.split("/@")[0]

            try:
                return [element.get_attribute(query_attribute) for element in
                        self.__driver.find_elements_by_xpath(xpath_query)]
            except NoSuchElementException:
                return None
        else:
            try:
                return self.__driver.find_elements_by_xpath(xpath_query)
            except NoSuchElementException:
                return None

    def get_element_code(self, element) -> str:
        """
        Given an HTML element return its HTML code.

        Args:
              element (WebElement): HTML element of Selenium WebElement type

        Returns:
            string HTML code
        """
        return " ".join(element.get_attribute('outerHTML').split())

    def get_element_text(self, element) -> str:
        """
        Returns visible text of HTML element. If string HTML element is passed it returns it. This makes this function
        able to be iteratively called on page parser elements even if they are returned as a mix of WebElements and str.

        Args:
              element (WebElement | str): HTML element of Selenium WebElement type which has attribute text or a string
              representation of HTML element

        Returns:
            string text content
        """
        if hasattr(element, 'text'):
            return " ".join(str(element.text).split())
        elif isinstance(element, str):
            return element

    def get_element_attribute(self, element: WebElement, attribute="textContent") -> str or None:
        """
        Given an HTML element and its attribute name, return attributes content.

        Args:
            element:  HTML element of Selenium WebElement type
            attribute: attribute name, defaults to textContent

        Returns:
            HTML element's attribute text value
        """
        if hasattr(element, "get_attribute"):
            return element.get_attribute(attribute)
        else:
            return None


class LXMLPageParser(AbstractPageParser):
    """ Web page parser with lxml core. """

    def __init__(self, url):
        super().__init__(url)
        page = requests.get(url)

        self.__tree = lxml.html.fromstring(page.text)
        self.source = " ".join(page.text.split())
        self.text = self.get_element_text(self.get_elements("/*")[0])
        self.base_url = get_base_url(self.text, url)
        title_el = self.get_elements("/html/head/title")
        title_el = title_el[0] if len(title_el) >= 1 else None
        self.title = self.get_element_text(title_el)
        description_el = self.get_elements("(/html/head/meta[@name='description'])")
        description_el = description_el[0] if len(description_el) >= 1 else None
        self.description = self.get_element_attribute(description_el, "content")

    def get_elements(self, xpath_query: str):
        """
        Get a list of HTML elements using xpath query on page parsed web page.

        Args:
            xpath_query (str): xpath elements query

        Returns: a list of lxml HtmlElement elements
        """
        return self.__tree.xpath(xpath_query)

    def get_element_code(self, element) -> str:
        """
        Given an HTML element return its HTML code.

        Args:
              element (HtmlElement): HTML element of lxml HtmlElement type

        Returns:
            string HTML code
        """
        return " ".join(str(lxml.etree.tostring(element)).split())

    def get_element_text(self, element) -> str:
        """
        Returns visible text of HTML element. If string HTML element is passed it returns it. This makes this function
        able to be iteratively called on page parser elements even if they are returned as a mix of HtmlElements and str.

        Args:
              element (HtmlElement | str): HTML element of lxml HtmlElement type which has method text_content() or a string
              representation of HTML element

        Returns:
            string text content
        """
        # remove all script elements from the tree
        if hasattr(element, 'findall') and hasattr(element, 'text_content'):
            [script_tag.drop_tree() for script_tag in element.findall('.//script')]
            [style_tag.drop_tree() for style_tag in element.findall('.//style')]
            return " ".join(str(element.text_content()).split())
        elif isinstance(element, str):
            return element

    def get_element_attribute(self, element: lxml.html.HtmlElement, attribute="textContent") -> str or None:
        """
        Given an HTML element and its attribute name, return attributes content.

        Args:
            element:  HTML element of lxml HtmlElement type
            attribute: attribute name, defaults to textContent

        Returns:
            HTML element's attribute text value
        """
        if attribute == "textContent":
            content = element.text
        else:
            content = element.get(attribute)
        return content if content else None
