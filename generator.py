import json
import time
import datetime
from collections import OrderedDict
from bs4 import BeautifulSoup
import os
import urllib.request
import sys
import HTBookwormCatalogGenerator.util as u
import HTBookwormCatalogGenerator.classification as c
import HTBookwormCatalogGenerator.location as loc
import logging
import argparse
import pysolr

# Get arguments
parser = argparse.ArgumentParser()
parser.add_argument("--hathifile", help="location of HathiFile to parse", type=str,
                    default = "hathifile.txt")
parser.add_argument("--outDir", default=os.getcwd())
parser.add_argument("--startLine", type=int, default = 0)
parser.add_argument("--endLine", type=int, default = -1)
parser.add_argument("--solrEndpoint", help="Which Solr endpoint should be queried for the API?",
                    type=str, default = "http://chinkapin.pti.indiana.edu:9994/solr/meta/")

args = parser.parse_args()

# Set up logger
logging.basicConfig(filename=os.path.join(args.outDir, "solr2bookwormCat.log"),
                    filemode="a", level=logging.DEBUG)
logging.info(args)

# Set up PySolr
solr = pysolr.Solr(args.solrEndpoint, timeout=10)

# Prepare Input/output files
cat = open(os.path.join(args.outDir, "jsoncatalog.txt"), 'w+')
hathi = open(args.hathifile, 'r')

lineNum = 1
# read in one line at a time, write out one json string at a time, logging progress
for line in hathi:
    if lineNum < args.startLine:
        lineNum += 1
        continue
    elif args.endLine > 0 and lineNum > args.endLine:
        break
    elif lineNum >= args.startLine:
        logging.info("reading line number " + str(lineNum))
        row = (line.split('\t'))
        institutionId = (row[0].split('.'))[0]
        cleanVolumeId = row[0].replace(':', "+")
        cleanVolumeId = cleanVolumeId.replace('/', "=")

        # use volume id from hathifile
        volumeId = row[0]

        # Set defaults for output metadata record
        record = {"date": row[16], "searchstring": "unknown", "lc_classes": [], "lc_subclass": [],
                  "fiction_nonfiction": "unknown", "genres": [], "languages":[], "format": "unknown",
                  "page_count_bin": "unknown", "word_count_bin": "unknown", 
                  "publication_place": "unknown", "filename": cleanVolumeId}
        
        # use publication_country from hathifile first
        record['publication_country'] = loc.marcCountryDict[row[17]] if row[17] in loc.marcCountryDict else "unknown"
        record['publication_state'] = loc.marcStateDict[row[17]] if row[17] in loc.marcStateDict else ""
        record['is_gov_doc'] = "Yes" if row[15] == 1 else "No"

        # set default values in case a value is not available from solr
        #serial = "unknown"
        #genders =[]
        #publicationDate = 0
        title = "unknown"

        # get information from Solr
        results = solr.search("id:%s" % row[0])
        print(list(results))
        if len(results) > 0:
            for result in results:
                if 'publishDate' in result:
                    record['date'] = int(result['publishDate'][0])

                if "callnumber" in result:
                    for callNumber in result['callnumber']:
                        classResponse = c.getClass(callNumber)
                        if classResponse is not None:
                            record['lc_classes'].append(c.getClass(callNumber))

                        subclassResponse = c.getSubclass(callNumber)
                        if subclassResponse is not None:
                            record['lc_subclass'].append(c.getSubclass(callNumber))

                if "genre" in result:
                    for genre in result['genre']:
                        if genre == 'Fiction':
                            record['fiction_nonfiction'] = 'Fiction'
                        elif genre == 'Not fiction':
                            record['fiction_nonfiction'] = 'Not fiction'
                        else:
                            record['genres'].append(genre)

                for key in ["format", "publication_place"]:
                    # Doublecheck that solr returned the field
                    if key in result:
                        record[key] = result[key][0]

                if "language" in result:
                    record['languages'] = result["language"] # Use the full list

                if "title_a" in result:
                    title = result['title_a'][0]

                if 'country_of_pub' in result and record['publication_country'] == "unknown":
                    record['publication_country'] = result['country_of_pub'][0]

                if 'htrc_pageCount' in result:
                    result['page_count_bin'] = u.getPageBin(int(result['htrc_pageCount']))
                
                if 'htrc_wordCount' in result:
                    result['word_count_bin'] = u.getPageBin(int(result['htrc_wordCount']))

            # add unknown value to empty arrays so they can be searched using filters
            for field in ['lc_classes', 'lc_subclass', 'genres', 'languages']:
                if len(record[field]) == 0:
                    record[field] = ['unknown']

            record['searchstring'] = "<a href='http://hdl.handle.net/2027/%s/'>%s</a>" % (volumeId, title)

            print(json.dumps(record))
            #json.dump(OrderedDict([('date', date),('searchstring', searchString),('lc_classes', lc_classes),('lc_subclass', lc_subclasses),('fiction_nonfiction', fiction_nonfiction),('genres', genres),('languages', languages),('format', form),('is_gov_doc',is_gov_doc),('page_count_bin', page_count_bin),('word_count_bin', word_count_bin),('publication_country', publication_country),('publication_state',publication_state),('publication_place', publication_place),('filename', filename)]), cat)
            cat.write('\n')

    lineNum+=1

cat.close()
hathi.close()
logging.info("done")

