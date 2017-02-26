# twg - The Wikipedia Graph

Uses the Python package scrapy to spider a category of pages on Wikipedia including subcategories.  The spider only outputs the pages themselves, and any pages that they link to.  The output is structured with a "from" value for the page that was found in the category tree, an array of "to" values representing the wiki pages that the "from" page links to, plus an "ext" array representing the links to external domains (i.e. outside of en.wikipedia.org).

The scrapy command line interface allows this data to be output in different formats.
