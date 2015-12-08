import requests
from bs4 import BeautifulSoup
import os
import json
import pymongo
from pymongo import MongoClient
import re
import sys

client = MongoClient('localhost', 27017)
db = client['micro_man']
collection = db['micro_man']


websites = []
websites_stats = {}

def build_site_list():
    for root, dirs, files in os.walk('/path/to/websites/directory'):
        for name in dirs:
            if name.endswith('.com'):
                websites.append(name)
                # if name contains "output" or "public" or ""

def crawl_sites(websites):
    with open('websites_stats.json', 'w') as fo:

        for site in websites:
            site_id = site.replace('.', '_')
            adcodes = {}
            print "Checking site: ", site
            page_count = False
            twitter_handle = False
            tumblr_domain = False
            url = 'http://www.' + site
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            i = soup.find_all(string=re.compile("googletag.defineSlot\('(.*)'\).addService\(googletag.pubads\(\)\);"))
            if i:
                print "Found ads."
                pattern = "defineSlot\('(.*)'\).addService"
                found_adcodes = re.findall(pattern, i[0])
                i = 1
                print found_adcodes
                for code in found_adcodes:
                    campaign = re.findall('\/(.*)\/', code)
                    size = re.findall('\[(.*)\]', code)
                    key = re.findall('div-gpt-ad-([0-9-]*)', code)
                    adcodes.update({ key[0]: {
                    "campaign": campaign[0],
                    "size": size[0],
                    "raw_code": code
                    }
                    })
                    i += 1
            else:
                print "Found nothing."

            stat = {
                 site_id: {
                    "domain": site,
                    "adcodes": adcodes,
                    "page_count": page_count,
                    "social_accounts": {
                        "twitter": twitter_handle,
                        "tumbler": tumblr_domain
                    }
                }
            }
            websites_stats.update(stat)
            stats = db.stats
            result = stats.insert_one(stat)
            print result

        content = websites_stats
        fo.write(json.dumps(content, indent=4, sort_keys=True))
        fo.close()


build_site_list()
crawl_sites(websites)
