# -*- coding: utf-8 -*-
""" This modules contains all of the predefined page checks. Page check works at single HTML page level.

Predefined page checks are enumerated in PageCheck enum with each enum value containing the name of the class
that implements the defined check by extending AbstractPageCheck class.

When functionality of predefined page checks is not enough, custom PageCheck can be created by extending
AbstractPageCheck class.

Typical usage example:

    url = "https://google.com"
    parser = LXMLPageParser(url)
    check = check_page(PageCheck.PAGE_CRAWLABLE, parser)

Todo:
    * move tokenization, stop words removal and stemming into helper module

"""

from enum import Enum
import abc
import sys
import string
from nltk import word_tokenize
import nltk
from collections import Counter
import extruct

from seoaudit.analyzer.page_parser import AbstractPageParser


class AbstractPageCheck(metaclass=abc.ABCMeta):
    """ Abstract class that serves as a blueprint for page check classes. """

    @abc.abstractmethod
    def check_page(self, parser: AbstractPageParser, **kwargs):
        """ Returns check validity of the given page.

        Args:
            parser (AbstractPageParser) : HTML page parser object
            *kwargs: keyword check arguments (e.g. a number representing a maximal tex to to code value)

        Returns:
            a boolean value representing checks validity preceded by any extra check result information
        """


class DOMSizeCheck(AbstractPageCheck):
    """ Checks if page DOM size (number of DOM element nodes) is smaller than a given maximal value. """

    def check_page(self, parser: AbstractPageParser, **kwargs):
        """

        Args:
            parser (AbstractPageParser) : HTML page parser object
            *kwargs: keyword check arguments that include 'max_size' parameter that defaults to 0

        Returns:
            a boolean value representing checks validity preceded by DOM size (number of HTML elements)
        """

        max_size = kwargs.get('max_size', 0)

        if max_size <= 0:
            return False

        return len(parser.get_elements("//*")) < max_size, len(parser.get_elements("//*"))


class TextToCodeRatioCheck(AbstractPageCheck):
    """ Checks if page Text-to-code (length of visible text divided by length of HTML code) ratio is bigger than a
    given minimal value. """

    def check_page(self, parser: AbstractPageParser, **kwargs):
        """

        Args:
            parser (AbstractPageParser) : HTML page parser object
            *kwargs: keyword check arguments that include 'min_ratio' parameter that defaults to 0

        Returns:
            a boolean value representing checks validity preceded by code-to-text ratio
        """
        min_ratio = kwargs.get('min_ratio', 0)

        if min_ratio <= 0:
            return True

        text_size = len(parser.text)
        code_size = len(parser.source)

        return (text_size / code_size) >= min_ratio, (text_size / code_size)


class ElementsSimilarityCheck(AbstractPageCheck):
    """ Checks if first element's most common top keywords are found in second element. Optionally
     first element's keywords are filtered with stopwords and stememed."""

    def check_page(self, parser: AbstractPageParser, **kwargs):
        """

        Args:
            parser (AbstractPageParser) : HTML page parser object
            *kwargs: keyword check arguments that include: 'el1_query' - xpath query for first element, 'el2_query'
            xpath query for second element, 'match_most_common' - number of most common keywords that are checked ,
             'stop_words' - optional list of stop words that are filtered on the first adn second element ,
             'stemmer' - optional nltk-like stemmer object that stems most common keywords before doing the check

        Returns:
            a boolean value representing checks validity

        Todo: remove any duplicates after stemming
        """
        el1_query = kwargs.get('el1_query')
        el2_query = kwargs.get('el2_query')
        match_most_common = int(kwargs.get('match_most_common'))

        if el1_query is None or not isinstance(el1_query, str):
            raise ValueError("Argument el1_query must be of type str.")

        if el2_query is None or not isinstance(el2_query, str):
            raise ValueError("Argument el2_query must be of type str.")

        if match_most_common is None:
            raise ValueError("Argument match_most_common must be of type int.")

        stop_words = kwargs.get('stop_words')
        stemmer = kwargs.get('stemmer')

        elements1 = parser.get_elements(el1_query)
        elements2 = parser.get_elements(el2_query)

        # if an empty element list is found for first or second element query return False
        if len(elements1) < 1 or len(elements2) < 1:
            return False

        element_1 = parser.get_element_text(elements1[0])
        element_2 = parser.get_element_text(elements2[0])

        table = str.maketrans('', '', string.punctuation)

        try:
            element_1_tokens = [w.lower() for w in word_tokenize(element_1)]
            element_2_tokens = [w.lower() for w in word_tokenize(element_2)]
        except LookupError:
            nltk.download('punkt')
            element_1_tokens = [w.lower() for w in word_tokenize(element_1)]
            element_2_tokens = [w.lower() for w in word_tokenize(element_2)]

        # remove all string punctuations
        element_1_tokens = [w.translate(table) for w in element_1_tokens]
        element_2_tokens = [w.translate(table) for w in element_2_tokens]
        # remove remaining tokens that are not alphabetic
        element_1_words = [word for word in element_1_tokens if word.isalpha()]
        element_2_words = [word for word in element_2_tokens if word.isalpha()]

        # filter out stop words i stopwords are defined
        if stop_words and all(isinstance(s, str) for s in stop_words):
            element_1_words = [w for w in element_1_words if not w in stop_words]
            element_2_words = [w for w in element_2_words if not w in stop_words]

        # stem words if stemmer object is defined
        if stemmer and hasattr(stemmer, 'stem'):
            element_1_words = [stemmer.stem(word) for word in element_1_words]
            element_2_words = [stemmer.stem(word) for word in element_2_words]

        element_1_dict = Counter(element_1_words)

        # if a keyword from most common first elements that deosnt exist in second element is found return False
        for w in element_1_dict.most_common(match_most_common):
            if w[0] not in element_2_words:
                return False, element_1_dict.most_common(match_most_common), element_2_words
        return True, element_1_dict.most_common(match_most_common), element_2_words


class ElementsCountCheck(AbstractPageCheck):
    """ Checks if elements count within a given interval. """

    def check_page(self, parser: AbstractPageParser, **kwargs):
        """
        Args:
            parser (AbstractPageParser) : HTML page parser object
            *kwargs: keyword check arguments that include 'min_count' parameter that defaults to 0 and 'max_count'
            parameter that defaults to sys.maxsize

        Returns:
            Tuple(boolean, int): tuple including boolean check result and elements count

        """
        query = kwargs.get('query')
        min_count = kwargs.get('min_count', 0)
        max_count = kwargs.get('max_count', sys.maxsize)

        if query is None or not isinstance(query, str):
            raise ValueError("Argument query must be of type str.")

        elements = parser.get_elements(query)
        return min_count <= len(elements) <= max_count, len(elements)


class StructuredDataFoundCheck(AbstractPageCheck):
    """ Checks if structured data is found in the page content. """

    def check_page(self, parser: AbstractPageParser, **kwargs):
        """
        If none of the kwargs arguments are set check returns True if any structured data is found.
        If type argument is set check returns True if any structured data of given type is found.
        If key argument is set check returns True if structured data is also filtered on predefined key.
        If key  and value arguments are set check filters structured data on defined key-value pair.

        Args:
            parser (AbstractPageParser) : HTML page parser object
            *kwargs: keyword check arguments that include 'type', 'key' and 'value' parameters. type' property can
            contain any of microdata', 'json-ld', 'opengraph','microformat' and 'rdfa'  values.
            While 'key' and 'value' arguments are used to filter structured data on given key, or key-value pair.

        Returns:
            Tuple(boolean, int): tuple including boolean check result and elements count

        """
        data = extruct.extract(parser.source, base_url=parser.base_url)

        sd_type = kwargs.get('type')
        sd_key = kwargs.get('key')
        sd_value = kwargs.get('value')

        if sd_type:
            data = data[sd_type]

            for data_element in data:
                if sd_key and sd_value and data_element[sd_key] == sd_value:
                    return True
                if sd_key and not sd_value and sd_key in data_element:
                    return True
                if not sd_key and not sd_value:
                    return True

            return False

        else:
            for data_type in data:
                for data_element in data_type:
                    if sd_key and sd_value and data_element[sd_key] == sd_value:
                        return True
                    if sd_key and not sd_value and sd_key in data_element:
                        return True
                    if not sd_key and not sd_value:
                        return True

            return False


class PageCheck(Enum):
    TEXT_TO_CODE_RATIO = TextToCodeRatioCheck
    DOM_SIZE = DOMSizeCheck
    ELEMENTS_SIMILARITY = ElementsSimilarityCheck
    ELEMENTS_COUNT = ElementsCountCheck
    STRUCTURED_DATA_FOUND = StructuredDataFoundCheck


def check_page(check: PageCheck, parser: AbstractPageParser, **kwargs):
    return check.value().check_page(parser, **kwargs)
