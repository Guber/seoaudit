# SEOAudit

SEO tool that analyzer a set of urls, crawls the pages and audits a set of predefiend checks element, page and site
 tests on them.

## Requirements

Python 3.6+ and modules 'requests', 'lxml', 'nltk', 'extruct', 'selenium'

## Installation

pip install seoaudit

## Using CLI

For analyzing a single site with default checks run with `seoaudit -u URL`, e.g.:
`seoaudit -u https://green-light.agency`

To define extra urls just add another `u URL` argument:
`seoaudit -u https://green-light.agency -u https://milenial.eu`

To use custom python checks config file (e.g. config.py) use option `-c PYTHON_MODULE`:
`seoaudit -u https://green-light.agency -c config`

To parse sitemap.xml for extra urls to parse add `-p`:
`seoaudit -u https://green-light.agency -p`

## Documentation

Extra documentation including API documentation and examples on extending the module with custom checks:

[SEOAudit documentation](https://seoaudit.readthedocs.io/ "SEOAudit documentation")