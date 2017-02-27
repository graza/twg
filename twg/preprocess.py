import json
import fileinput

pages = dict()
for line in fileinput.input():
    page = json.loads(line)
    pages[page["from"]] = page["to"]

for (page, old_to) in pages.items():
    new_to = list()
    for to_page in old_to:
        if to_page in pages:
            new_to.append(to_page)
    pages[page] = new_to

print(json.dumps(pages, sort_keys = True, indent = 4, ensure_ascii=False))
