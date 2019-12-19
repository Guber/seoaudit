Using CLI script
**************************

Using CLI

-----------------

For analyzing a single site with default checks run with `seoaudit -u URL`, e.g.:
`seoaudit -u https://green-light.agency`

To define extra urls just add another `u URL` argument:
`seoaudit -u https://green-light.agency -u https://milenial.eu`

To use custom python checks config file (e.g. config.py) use option `-c PYTHON_MODULE`:
`seoaudit -u https://green-light.agency -c config`

To parse sitemap.xml for extra urls to parse add `-p`:
`seoaudit -u https://green-light.agency -p`


Custom config
-----------------

TODO: add custom config definition


Extending predefined checks
-----------------

TODO: Extending predefined checks