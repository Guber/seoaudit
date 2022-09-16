import argparse

from seoaudit.analyzer.site_parser import SiteParser, LXMLPageParser
from seoaudit.analyzer.seo_auditor import SEOAuditor

def main():
    """The main routine."""
    parser = argparse.ArgumentParser(description='Run SEO checks on a set of urls')

    parser.add_argument('-u', '--url', action='append', help='<Required> Url to parse', required=True)
    parser.add_argument('-c', '--config', help='Python config file to use (without file extension)')
    parser.add_argument('-s', '--sitemap', help='Sitemap location', default=None)
    parser.add_argument('-p', '--parse', action="store_true", help='Parse sitemap urls', default=False)

    args = parser.parse_args()

    # Load the configuration file
    if args.config:
        import importlib
        import os

        try:
            module_name = args.config
            module_file_path = os.path.abspath(os.getcwd()) + "\\" + module_name + ".py"
            module_spec = importlib.util.spec_from_file_location(
                module_name, module_file_path)
            cfg = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(cfg)

            print("Using config file {}".format(args.config))
        except ImportError as err:
            print('Error:', err)
    else:
        import seoaudit.config as cfg
        print("Using default conf file")

    # site_parser = SiteParser(url,  SeleniumPageParser(url))
    print("Starting Site Parser...")
    site_parser = SiteParser(args.url[0], LXMLPageParser(args.url[0]), urls=args.url, sitemap_link=args.sitemap,
                             parse_sitemap_urls=args.parse)

    # initiate auditer object
    print("Starting SEO Auditor...")
    print("-----------------------")

    auditer = SEOAuditor(args.url[0], site_parser, cfg.page_tests, cfg.element_tests)
    auditer.run_checks_for_site()

    print("-----------------------")
    print("SEO Auditor finished.")
    print("Results stored in: {} and {}".format(auditer.result_filename, auditer.result_filename.replace('.json',
                                                                                                         '.html')))


if __name__ == "__main__":
    main()
