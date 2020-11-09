# SEOAudit

SEO tool for analyzing a set of urls, crawls the pages and audits a set of predefined checks element, page and site
 tests on them.
 
### Main features

- Python3 CLI script with JSON (and soon HTML) reports
- Python3 API
- Open-source project: https://github.com/Guber/seoaudit
- Tests configurable and parameterized

### Why yet another SEO tool?
SEO (Search Engine Optimization) is a set of activities with a goal to
increase organic traffic from search engines to the website.
On-page SEO (as oppsed to off-site SEO) is a set of on-page optimizations such as optimization of the HTML tags used, 
content quality, speed, etc.

SEOaudit is an **on-site SEO tool** that differs to other SEO tools i na way that 
it is **completely configurable**, **interoperable** into development environment either as a CLI 
script or through its API usage and it is **completely free**!

## Requirements

Python 3.6+ and modules `requests`, `lxml`, `nltk`, `extruct`, `selenium`.

## Installation

To install run: `pip install seoaudit`.

## Using CLI

For analyzing a single site with default checks run with `seoaudit -u URL`, e.g.:
`seoaudit -u https://green-light.agency`.

To define extra urls just add another `u URL` argument:
`seoaudit -u https://green-light.agency -u https://milenial.eu`.

To use custom python checks config file (e.g. config.py) use option `-c PYTHON_MODULE`:
`seoaudit -u https://green-light.agency -c config`.

To parse sitemap.xml for extra urls to parse add `-p`:
`seoaudit -u https://green-light.agency -p`.

## Documentation

Extra documentation including API documentation and examples on extending the module with custom checks:
[SEOAudit documentation](https://seoaudit.readthedocs.io/ "SEOAudit documentation").