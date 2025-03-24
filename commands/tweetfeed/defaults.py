#!/usr/bin/env python3

BINDS = ['@tweetfeed']
CHANS = ['debug']
# You can change the 'week' part of the APIURL to a different timeframe, if so desired.
APIURL = {
    'tweetfeed':   {'url': 'https://api.tweetfeed.live/v1/week',}
}
CONTENTTYPE = 'application/json'
LIMIT = 20
HELP = {
    'DEFAULT': {
        'args': '<any IP, domain, URL, SHA256 or MD5>',
        'desc': 'Query the Tweetfeed API for the given IP, domain, URL, SHA256 or MD5. By default, '
                'the information from the last month is checked. This can be changed in the config '
                'file.',
    },
}