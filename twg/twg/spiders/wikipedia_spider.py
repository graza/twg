import scrapy
import re
import urllib.parse

# The purpose of this spider is to output the links between
# pages within a given category on Wikipedia.
#
# The spider starts from a category and recurses into all
# linked subcategories.  It also fetches the linked pages
# using a different parser which generates the output of
# the links between pages.
class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"

    # The start request is the named category page
    def start_requests(self):
        url = 'https://en.wikipedia.org/wiki/Category:Mathematics'
        category = getattr(self, 'category', 'Algebraists')
        url = 'https://en.wikipedia.org/wiki/Category:' + category
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        self.log('Got page for URL %s' % response.url)

        # Fetch and recurse into all subcategories
        for subcat in response.css('#mw-subcategories a'):
            subcat_link = subcat.css('::attr(href)').extract_first()
            if subcat_link is not None:
                self.log('Recursing to subcategory %s' % subcat.css('::text').extract_first())
                subcat_link = response.urljoin(subcat_link)
                yield scrapy.Request(subcat_link, callback=self.parse)

        # Fetch all pages linked
        for page in response.css('#mw-pages a'):
            #self.log('******** RAW URL %s' % page.css('::attr(href)').extract_first())
            page_link = page.css('::attr(href)').re_first(r'[^#]+')
            #page_url = urllib.parse.urlparse(page_link)
            if page_link is not None and re.search(r":", page_link) is None:
                self.log('Recursing to page %s (%s)' % (page.css('::text').extract_first(), page_link))
                page_link = response.urljoin(page_link)
                yield scrapy.Request(page_link, callback=self.parse_page)

    # Function to strip the path down to something human readable
    def path_to_title(self, path):
        path = re.match(r"^/wiki/(.*)", path).group(1)
        path = urllib.parse.unquote(path)
        path = re.sub(r"_", " ", path)
        #self.log('Path is now %s' % path)
        return path

    def parse_page(self, response):
        self.log('Got page for URL %s' % response.url)
        links = set()
        ext = set()
        resp_url = urllib.parse.urlparse(response.url)
        for link in response.css('#mw-content-text a'):
            link = response.urljoin(link.css('::attr(href)').re_first(r'[^#]+'))
            link_url = urllib.parse.urlparse(link)
            # Links to external domains are noted in ext set by their domain only
            if link_url.netloc != resp_url.netloc:
                ext.add(link_url.netloc)
            # We don't want loops, nor non-Wiki pages, nor other meta pages with colon (e.g. Help:)
            elif link != response.url and re.match(r"^/wiki/[A-Z0-9]{1}", link_url.path) and re.search(r":", link_url.path) is None:
                # Add the wikipedia page name
                links.add(self.path_to_title(link_url.path))
        yield {
            "from": self.path_to_title(resp_url.path),
            "to":   list(links),
            "ext":  list(ext)
        }