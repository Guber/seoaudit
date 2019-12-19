#!/usr/bin/env python
from seoaudit.checks.element import ElementCheck
from seoaudit.checks.page import PageCheck
from seoaudit.checks.site import SiteCheck

page_tests = [(PageCheck.TEXT_TO_CODE_RATIO, {"min_ratio": 0.1}),
              (PageCheck.DOM_SIZE, {"max_size": 1500}),
              [PageCheck.ELEMENTS_SIMILARITY,
               {"el1_query": "/*", "el2_query": "/html/head/title", "match_most_common": 5}],
              [PageCheck.ELEMENTS_SIMILARITY,
               {"el1_query": "/*", "el2_query": "/html/head/meta[@name='description']/@content",
                "match_most_common": 5}],
              [PageCheck.ELEMENTS_SIMILARITY,
               {"el1_query": "//h1", "el2_query": "/html/head/meta[@name='description']/@content",
                "match_most_common": 5}],
              [PageCheck.ELEMENTS_COUNT, {"query": "(//h2)", "min_count": 2}],
              [PageCheck.STRUCTURED_DATA_FOUND, {"type": "json-ld", "property": "@type", "value": "Organization"}],
              [SiteCheck.TITLE_REPETITION],
              [SiteCheck.DESCRIPTION_REPETITION],
              [SiteCheck.PAGE_IN_SITEMAP],
              [SiteCheck.PAGE_CRAWLABLE]]

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
    ("(/html/head/meta[@property='og:locale'])", 'content'),
    ("(/html/head/meta[@property='og:title'])", 'content'),
    ("(/html/head/meta[@property='og:description'])", 'content'),
    ("(/html/head/meta[@property='og:type'])", 'content'),
    ("(/html/head/meta[@property='og:url'])", 'content'),
    ("(/html/head/meta[@property='og:image'])", 'content'),
    ("(/html/head/meta[@name='twitter:title'])", 'content'),
    ("(/html/head/meta[@name='twitter:description'])", 'content'),
    ("(/html/head/meta[@name='twitter:image'])", 'content'),
    ("(/html/head/meta[@name='twitter:card'])", 'content'),
    ("(/html/head/link[@rel='canonical'])", 'href')
]
