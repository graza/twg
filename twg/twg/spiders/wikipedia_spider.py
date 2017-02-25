import scrapy
import re
import urlparse

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
            if page_link is not None and re.search(r":", page_link) is None:
                self.log('Recursing to page %s (%s)' % (page.css('::text').extract_first(), page_link))
                page_link = response.urljoin(page_link)
                yield scrapy.Request(page_link, callback=self.parse_page)

    def parse_page(self, response):
        self.log('Got page for URL %s' % response.url)
        links = set()
        url = urlparse(response.url)
        for link in response.css('#mw-content-text a'):
            link_link = response.urljoin(link.css('::attr(href)').re_first(r'[^#]+'))
            if link_link is not None and link_link != response.url:
                links.add(link_link)
        yield {"from": response.url, "to": list(links)}