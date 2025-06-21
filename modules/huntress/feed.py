#!/usr/bin/env python3

# Every module must set the CHANNELS variable to indicate where information should be sent to in Mattermost
#
# Every module must implement the query() function.
# This query() function is called by the main worker and has only one parameter: the number of historic
# items that should be returned in the list.
#
# Every module must return a list [...] with 0, 1 ... n entries
# of 2-tuples: ('<channel>', '<content>')
#
# <channel>: basically the destination channel in Mattermost, e.g. 'Newsfeed', 'Incident', etc.
# <content>: the content of the message, MD format possible

import bs4
import feedparser
import re
import requests
from pathlib import Path
try:
    from modules.huntress import defaults as settings
except ModuleNotFoundError: # local test run
    import defaults as settings
    if Path('settings.py').is_file():
        import settings
else:
    if Path('modules/huntress/settings.py').is_file():
        try:
            from modules.huntress import settings
        except ModuleNotFoundError: # local test run
            import settings

def checkPage(link):
    try:
        with requests.Session() as session: 
            response = session.get(link, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                })
                # 'User-Agent': 'MatterBot RSS Automation 1.0'
            response.raise_for_status()
            data = bs4.BeautifulSoup(response.content, "html.parser")
            matches = data.select('a.category-sidebar-item[href="/blog-categories/threat-analysis"]') # Check if article is of category threat-analysis 
    except requests.exceptions.RequestException:
        matches = False
    return matches

def query(MAX=settings.ENTRIES):
    items = []
    feed = feedparser.parse(settings.URL, agent='MatterBot RSS Automation 1.0')
    count = 0
    stripchars = '`\\[\\]\'\"'
    regex = re.compile('[%s]' % stripchars)
    while count < MAX:
        try:
            title = feed.entries[count].title
            link = feed.entries[count].link
            matches = checkPage(link)
            if matches:
                content = settings.NAME + ': [' + title + '](' + link + ')'
                if len(feed.entries[count].description):
                    description = regex.sub('',bs4.BeautifulSoup(feed.entries[count].description,'lxml').get_text("\n")).strip().replace('\n','. ')
                    if len(description)>400:
                        description = description[:396]+' ...'
                    content += '\n>'+description+'\n'
                for channel in settings.CHANNELS:
                    items.append([channel, content])
            count+=1
        except IndexError:
            return items # No more items
    return items

if __name__ == "__main__":
    print(query())
