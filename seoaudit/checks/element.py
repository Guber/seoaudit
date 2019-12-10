# -*- coding: utf-8 -*-
""" This modules contains all of the predefined element checks. Element check works at single DOM element level.


Predefined element checks are enumerated in ElementCheck enum with each enum value containing the name of the class
that implements the defined check by extending AbstractElementCheck class.

When functionality of predefined element checks is not enough, custom ElementCheck can be created by extending
AbstractElementCheck class.

Typical usage example:

    content = "abc"
    check = check_content(ElementCheck.MIN_LENGTH, "abc", 2) # check = True
    check = check_content(ElementCheck.MIN_LENGTH, "abc", 4) # check = False

Todo:
    * element content keyword match check

"""

from enum import Enum
import abc
import re


class AbstractElementCheck(metaclass=abc.ABCMeta):
    """ Abstract class that serves as a blueprint for element check classes. """

    @abc.abstractmethod
    def check_content(self, content: str, **kwargs):
        """ Returns check validity of the given element.

        Args:
            content (str) : element content value on which check is performed
            *kwargs: keyword check arguments (e.g. a number representing a minimal length value)

        Returns:
             a boolean value representing checks validity preceded by any extra check result information
        """
        pass


class AttributeFoundCheck(AbstractElementCheck):
    """ Checks if content attribute is found and not empty. """

    def check_content(self, content: str, **unused):
        """
        Args:
            content: element content value on which check is performed
            unused: unused parameter defined to extend AbstractElementCheck

        Returns:
            boolean check result

        """
        return content is not None and len(content) > 0


class MinLengthCheck(AbstractElementCheck):
    """ Check if content length is bigger or equal to minimal length. """

    def check_content(self, content: str, **kwargs):
        """

        Args:
            content: element content value on which check is performed
            kwargs: keyword arguments (map) that includes 'min_length' parameter which defaults to 0 if not defined

        Returns:
             Tuple(boolean, int): tuple including boolean check result and content length

        """
        min_length = kwargs.get('min_length', 0)

        if min_length <= 0:
            return True

        return len(content) >= min_length, len(content)


class MaxLengthCheck(AbstractElementCheck):
    """ Check if content length is smaller or equal to maximal length.. """

    def check_content(self, content: str, **kwargs):
        """
        Args:
            content: element content value on which check is performed
            kwargs: keyword arguments (map) that includes 'max_length' parameter which defaults to 0 if not defined

        Returns:
            Tuple(boolean, int): tuple including boolean check result and content length

        """
        max_length = kwargs.get('max_length', 0)

        if max_length <= 0:
            return False

        return len(content) <= max_length, len(content)


class RegexMatchCheck(AbstractElementCheck):
    """ Implements content regex match check. """

    def check_content(self, content: str, **kwargs):
        """
        Args:
            content: element content value on which check is performed
            kwargs: keyword argument (map) that includes 'regex' parameter which defaults to '.*' if not defined
        Returns:
             Tuple(boolean, int): tuple including boolean check result and content length

        """
        regex = kwargs.get('regex', '.*')
        return re.match(regex, content)


class ElementCheck(Enum):
    """ Enum representing all of the predefined element check types. """
    ATTRIBUTE_FOUND = AttributeFoundCheck
    MIN_LENGTH = MinLengthCheck
    MAX_LENGTH = MaxLengthCheck
    CONTENT_REGEX_MATCH = RegexMatchCheck


def check_content(check: ElementCheck, content: str, **kwargs):
    """ Wrapper function to perform a check defined by the given ElementCheck.

    Args:
        check (ElementCheck): Enum identifying type of the check
        content (str) : element content value on which check is performed
        *kwargs: various content check arguments (e.g. a number representing a minimal length value)

    Returns:
        a boolean value representing checks validity preceded by any extra check result information
    """
    return check.value().check_content(content, **kwargs)
