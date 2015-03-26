import json
import time
import datetime
from collections import OrderedDict
from bs4 import BeautifulSoup
import os
import sys
import HTBookwormCatalogGenerator.util as u
import HTBookwormCatalogGenerator.classification as c
import HTBookwormCatalogGenerator.location as loc
import logging
import argparse
import pysolr
import re
import sys

def main():
    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("hathifile", nargs="?", help="location of HathiFile to parse", 
                        type=argparse.FileType('r', encoding='utf-8'), default=sys.stdin)
    parser.add_argument("--outfile", nargs="?", help="Location to save output metadata. Bookworm wants jsoncatalog.txt, default is stdout.", 
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument("--outDir", default=os.getcwd())
    parser.add_argument("--startLine", type=int, default = 0)
    parser.add_argument("--endLine", type=int, default = -1)
    parser.add_argument("--solrEndpoint", help="Which Solr endpoint should be queried for the API?",
                        type=str, default = "http://chinkapin.pti.indiana.edu:9994/solr/meta/")

    args = parser.parse_args()

    # Set up logger
    logging.basicConfig(filename=os.path.join(args.outDir, "solr2bookwormCat.log"),
                        filemode="a", level=logging.INFO) # Change to LOGGING.DEBUG for verbose msgs
    logging.info(args)

    # Set up PySolr
    solr = pysolr.Solr(args.solrEndpoint, timeout=10)

    # Set defaults for output metadata record

    lineNum = 0
    volids = [] # list for collecting volume IDs to search in batches
    records = {}
    batch_size = 20
    # read in one line at a time, write out one json string at a time, logging progress
    for line in args.hathifile:
        lineNum+=1
        if lineNum < args.startLine:
            continue
        elif args.endLine > 0 and lineNum > args.endLine:
            break
        elif lineNum >= args.startLine:
            logging.debug("reading line number " + str(lineNum))
            row = (line.split('\t'))
            institutionId = (row[0].split('.'))[0]
            cleanVolumeId = row[0].replace(':', "+")
            cleanVolumeId = cleanVolumeId.replace('/', "=")

            # use volume id from hathifile
            volumeId = row[0]
            volids += [volumeId]
            
            record = {"searchstring": "unknown", "lc_classes": [], "lc_subclass": [],
              "fiction_nonfiction": "unknown", "genres": [], "languages":[], "format": "unknown",
              "page_count_bin": "unknown", "word_count_bin": "unknown", 
              "publication_place": "unknown"}

            # Hathifile derived record info
            record['date'] = row[16]
            record['filename'] = cleanVolumeId
            record['publication_country'] = loc.marcCountryDict[row[17]] if row[17] in loc.marcCountryDict else "unknown"
            record['publication_state'] = loc.marcStateDict[row[17]] if row[17] in loc.marcStateDict else ""
            record['is_gov_doc'] = "Yes" if row[15] == 1 else "No"

            # Save record to records object, where we'll hold it until we query the Solr
            records[volumeId] = record

            # set default values in case a value is not available from solr
            #serial = "unknown"
            #genders =[]
            #publicationDate = 0

            if len(volids) >= batch_size:
                logging.info("%d records collected, Querying solr now." % batch_size)
                results = querySolr(volids, solr, batch_size)
                for result in results:
                    htfile_record = records[result['id']]
                    record = build_record(result['id'], result, htfile_record)
                    args.outfile.write(json.dumps(record)+'\n')
                volids = []
                records = {}

    # Process any outstanding files
    results = querySolr(volids, solr, batch_size)
    for result in results:
        htfile_record = records[result['id']]
        record = build_record(volumeId, result, htfile_record)
        args.outfile.write(json.dumps(record)+'\n')

    logging.info("done")

def querySolr(volids, solr, rows):
    ''' Queries multiple solr ids at once. Returns empty list when there are no results.'''
    if len(volids) == 0:
        return []

    # Make volume ids into query string
    q = "id:(%s)" % " ".join([re.escape(volid) for volid in volids])

    # get information from Solr
    try:
        results = solr.search(q, rows=rows)
    except Exception:
        logging.exception("Problem with search for \"%s\"" % q)
        return []
    logging.debug(list(results))

    if len(results) == 0:
        return []
    return results 
    

def build_record(volumeId, result, record):
    ''' 
    Process Solr API results
    results : JSON object of results from Solr
    records : object of HATHI derived record information, to augment with Solr info and
              write to jsoncatalog.txt
    '''

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
    else:
        title = "unknown"

    if 'country_of_pub' in result and record['publication_country'] == "unknown":
        record['publication_country'] = result['country_of_pub'][0]

    if 'htrc_pageCount' in result:
        record['page_count_bin'] = u.getPageBin(int(result['htrc_pageCount']))
    
    if 'htrc_wordCount' in result:
        record['word_count_bin'] = u.getWordBin(int(result['htrc_wordCount']))

    
    multi_fields = ["htsource","mainauthor","publisher","format","htrc_gender"]
    
    for field in multi_fields:
        try:
            record[field] = result[field]
        except KeyError:
            record[field] = []

    for field in ['lc_classes', 'lc_subclass', 'genres', 'languages'] + multi_fields:
        # eliminate duplicates
        record[field] = list(set(record[field]))
        # add unknown value to empty arrays so they can be searched using filters
        if len(record[field]) == 0:
            record[field] = ['unknown']

    record['searchstring'] = "<a href='http://hdl.handle.net/2027/%s'>%s</a>" % (volumeId, title)


    return record

if __name__ == '__main__':
    main()
