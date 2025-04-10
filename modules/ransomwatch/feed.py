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

import re
import requests
import shelve
import traceback
from pathlib import Path
try:
    from modules.ransomwatch import defaults as settings
except ModuleNotFoundError: # local test run
    import defaults as settings
    if Path('settings.py').is_file():
        import settings
else:
    if Path('modules/ransomwatch/settings.py').is_file():
        try:
            from modules.ransomwatch import settings
        except ModuleNotFoundError: # local test run
            import settings

def query(MAX=settings.ENTRIES):
    items = []
    try:
        if Path(settings.HISTORY).is_file():
            history = shelve.open(settings.HISTORY,writeback=True)
        else:
            if Path('modules/ransomwatch/'+settings.HISTORY).is_file():
                history = shelve.open('modules/ransomwatch/'+settings.HISTORY,writeback=True)
        if not Path(settings.HISTORY).is_file() and not Path('modules/ransomwatch/'+settings.HISTORY).is_file():
            if Path('feed.py').is_file():
                history = shelve.open(settings.HISTORY,writeback=True)
            else:
                if Path('modules/ransomwatch/feed.py').is_file():
                    history = shelve.open('modules/ransomwatch/'+settings.HISTORY,writeback=True)
        if not 'ransomwatch' in history:
            history['ransomransomwatch'] = []
        with requests.get(settings.URL) as response:
            feed = response.json()
        entries = sorted(feed, key=lambda feed: feed['discovered'], reverse=True)[:MAX]
        if len(entries):
            count = 0
            content = '**%s Update**\n' % (settings.NAME,)
            content += '\n| **Group** | **Victim** | **Publication** |'
            content += '\n| :- | :- | -: |'
            for entry in entries:
                victim = entry['post_title'].replace('&amp;','&').replace('&amp;','&').strip('\r\n')
                group = entry['group_name'].replace('&amp;','&').replace('&amp;','&').strip('\r\n').title()
                date = entry['discovered'].split('.')[0].strip(' \r\n')
                if re.search(r"^(((?!\-))(xn\-\-)?[a-z0-9\-_]{0,61}[a-z0-9]{1,1}\.)*(xn\-\-)?([a-z0-9\-]{1,61}|[a-z0-9\-]{1,30})\.[a-z]{2,}$", victim.lower()) or 'http' in victim:
                    victim = '[%s](%s)' % (victim, victim)
                else:
                    victim = victim.title()
                line = '\n| %s | %s | %s |' % (group, victim, date)
                if not line in history['ransomwatch']:
                    history['ransomwatch'].append(line)
                    content += line
                    count += 1
            content += '\n\n'
            if count>0:
                for channel in settings.CHANNELS:
                    items.append([channel, content])
        history.sync()
        history.close()
    except Exception as e:
        return items
    finally:
        return items

if __name__ == "__main__":
    print(query())
