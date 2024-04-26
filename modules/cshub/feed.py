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
import traceback
from pathlib import Path
try:
    from modules.cshub import defaults as settings
except ModuleNotFoundError: # local test run
    import defaults as settings
    if Path('settings.py').is_file():
        import settings
else:
    if Path('modules/cshub/settings.py').is_file():
        try:
            from modules.cshub import settings
        except ModuleNotFoundError: # local test run
            import settings

def query(MAX=settings.ENTRIES):
    items = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Content-type': 'application/rss+xml',
    }
    for category in settings.CATEGORIES:
        try:
            with requests.get("https://www.cshub.com/rss/categories/"+category,headers=headers) as response:
                feed = feedparser.parse(response.content)
                count = 0
                stripchars = '`\\[\\]\'\"'
                regex = re.compile('[%s]' % stripchars)
                while count < MAX:
                    try:
                        title = feed.entries[count].title
                        link = feed.entries[count].link
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
        except Exception as e:
            content = traceback.format_exc()
            for channel in settings.CHANNELS:
                items.append([channel, content])
    return items

if __name__ == "__main__":
    print(query())
