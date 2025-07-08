#!/usr/bin/env python3

import collections
import json
import re
import requests
import sys
import traceback
from pathlib import Path
try:
    from commands.lolrmm import defaults as settings
except ModuleNotFoundError: # local test run
    import defaults
    import defaults as settings
    if Path('settings.py').is_file():
        import settings
else:
    from commands.lolrmm import defaults
    if Path('commands/lolrmm/settings.py').is_file():
        try:
            from commands.lolrmm import settings
        except ModuleNotFoundError: # local test run
            import defaults
            import settings

def process(command, channel, username, params, files, conn):
    messages = []
    try:
        if len(params):
            stripchars = ' `\n\r\'\"'
            regex = re.compile('[%s]' % stripchars)
            headers = {
                'Content-Type': settings.CONTENTTYPE,
            }
            query = params[0]
            if query == 'rebuildcache' or not Path(settings.CACHE).is_file():
                with requests.get(settings.APIURL['lolrmm']['url'], headers=headers) as response:
                    json_response = response.json()
                    if len(json_response):
                        with open(settings.CACHE, mode='w') as f:
                            cache = json.dumps(json_response)
                            f.write(cache)
                            message = "LOLRMM cache rebuilt."
                            messages.append({'text': message})
            if Path(settings.CACHE).is_file() and len(query)>=4:
                with open(settings.CACHE,'r') as f:
                    lolrmms = json.load(f)
                results = []
                query = query.lower()
                for lolrmm in lolrmms:
                    found = False
                    if query in lolrmm['Name'].lower() or \
                        query in lolrmm['Description'].lower():
                        found = True
                    networkartifacts = set()
                    if 'Network' in lolrmm['Artifacts']:
                        if lolrmm['Artifacts']['Network']:
                            if len(lolrmm['Artifacts']['Network']):
                                for networkartifact in lolrmm['Artifacts']['Network']:
                                    if len(networkartifact['Domains']):
                                        for domain in networkartifact['Domains']:
                                            networkartifacts.add(domain)
                                        if query in [_.lower() for _ in networkartifacts]:
                                            found = True
                    if 'Disk' in lolrmm['Artifacts']:
                        if lolrmm['Artifacts']['Disk']:
                            if len(lolrmm['Artifacts']['Disk']):
                                if lolrmm['Artifacts']['Disk']:
                                    for diskartifact in lolrmm['Artifacts']['Disk']:
                                        if 'File' in diskartifact:
                                            if query in diskartifact['File'].lower() or \
                                                query in diskartifact['Description'].lower():
                                                found = True
                    if 'Registry' in lolrmm['Artifacts']:
                        if lolrmm['Artifacts']['Registry']:
                            if len(lolrmm['Artifacts']['Registry']):
                                for registrypathlist in lolrmm['Artifacts']['Registry']:
                                    if query in registrypathlist['Path'].lower():
                                        found = True
                    if 'InstallationPaths' in lolrmm['Details']:
                        if lolrmm['Details']['InstallationPaths']:
                            if len(lolrmm['Details']['InstallationPaths']):
                                if query in " ".join(lolrmm['Details']['InstallationPaths']).lower().replace('*',''):
                                    found = True
                    if found:
                        name = lolrmm['Name'].replace('\n','. ').replace('|','-').replace('\\','')
                        description = lolrmm['Description'].replace('\n','. ').replace('|','-').replace('\\','')
                        timestamp = lolrmm['LastModified']
                        url = "https://lolrmm.io/tools/%s" % (name.lower().replace(' ','_').replace('(','_').replace(')','_'),)
                        results.append(collections.OrderedDict({
                            'Name': name,
                            'Description': description,
                            'Updated': timestamp,
                            'Details': url,
                        }))
                if len(results):
                    message =  '**LOLRMM** search results for: `%s`\n' % (query,)
                    message += '\n| **Name** | **Description** | **Updated** | **Details** |'
                    message += '\n| :- | :- | -: | :- |'
                    for result in results:
                        message += f"\n| {result['Name']} | {result['Description']} | {result['Updated']} | [Link]({result['Details']}) |"
                    message += '\n\n'
                    messages.append({'text': message})
    except Exception as e:
        messages.append({'text': 'An error occurred in LOLRMM:\nError: ' + (str(e),traceback.format_exc())})
    finally:
        return {'messages': messages}
