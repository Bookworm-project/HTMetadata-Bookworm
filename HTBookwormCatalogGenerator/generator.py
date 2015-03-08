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

solrEndpoint = "http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:"

# Get arguments
parser = argparse.ArgumentParser()
parser.add_argument("--hathifile", help="location of HathiFile to parse", type=str,
                    default = "hathifile.txt")
parser.add_argument("--outDir", default=os.getcwd())
parser.add_argument("--startLine", type=int, default = 0)
parser.add_argument("--endLine", type=int, default = -1)

args = parser.parse_args()

# Set up logger
logging.basicConfig(filename=os.path.join(args.outDir, "solr2bookwormCat.log"),
                    filemode="a", level=logging.DEBUG)
logging.info(args)

# Prepare Input/output files
cat = open(os.path.join(args.outDir, "jsoncatalog.txt"), 'w+')
hathi = open(args.hathifile, 'r')

lineNum = 1
# read in one line at a time, write out one json string at a time, logging progress
for line in hathi:
    if args.endLine > 0 and lineNum > args.endLine:
        break
    elif lineNum < args.startLine:
        break
    elif lineNum >= args.startLine:
        logging.info("reading line number " + str(lineNum))
        row = (line.split('\t'))
        institutionId = (row[0].split('.'))[0]
        cleanVolumeId = row[0].replace(':', "+")
        cleanVolumeId = cleanVolumeId.replace('/', "=")

        # use volume id from hathifile
        volumeId = row[0]

        # use publication_country from hathifile
        publication_country = ""
        if row[17] in loc.marcCountryDict:
            publication_country = loc.marcCountryDict[row[17]]
        else:
            publication_country = "unknown"

        if row[17] in loc.marcStateDict:
            publication_state = loc.marcStateDict[row[17]]
        else:
            publication_state = ""

        # set default values in case a value is not available from solr
        searchString = "unknown"
        lc_classes = []
        lc_subclasses = []
        fiction_nonfiction = "unknown"
        genres = []
        languages = []
        serial = "unknown"
        genders =[]
        page_count_bin = "unknown"
        word_count_bin = "unknown"
        filename = cleanVolumeId
        publicationDate = 0
        title = "unknown"
        publication_place = "unknown"
        date = row[16]
        if row[15] == 1:
            is_gov_doc = "Yes"
        else:
            is_gov_doc = "No"

        # get information from Solr
        solrRequest = urllib.request.Request(solrEndpoint + row[0])
        solrResponse = urllib.request.urlopen(solrRequest)
        soup = BeautifulSoup(solrResponse.read())
        resultTag = soup.result
        numFound = resultTag.attrs['numfound']
        if u.is_int(numFound) and int(numFound) > 0:
            #handle the arr elements
            arrList = soup.find_all(name="arr")
            for arr in arrList:

                if arr['name'] == "publishDate":
                    if u.is_int(arr.contents[0].string):
                        date = int(arr.contents[0].string)

                elif arr['name'] == "callnumber":
                    callNumberArr = arr.contents
                    for callNumber in callNumberArr:
                        classResponse = c.getClass(callNumber.string)
                        if classResponse is not None:
                            lc_classes.append(c.getClass(callNumber.string))

                        subclassResponse = c.getSubclass(callNumber.string)
                        if subclassResponse is not None:
                            lc_subclasses.append(c.getSubclass(callNumber.string))

                elif arr['name'] == "genre":
                    genreArr = arr.contents
                    for genre in genreArr:
                        if genre.string == 'Fiction':
                            fiction_nonfiction = 'Fiction'
                        elif genre.string == 'Not fiction':
                            fiction_nonfiction = 'Not fiction'
                        else:
                            genres.append(genre.string)

                elif arr['name'] == "language":
                    languageArr = arr.contents
                    for language in languageArr:
                        languages.append(language.string)

                elif arr['name'] == "format":
                    form = arr.contents[0].string

                elif arr['name'] == "title_a":
                    title = arr.contents[0].string

                elif arr['name'] == "country_of_pub":
                    if publication_country == "unknown":
                        publication_country = arr.contents[0].string

                elif arr['name'] == "publication_place":
                    publication_place = arr.contents[0].string


            # handle named int elements (not children of arr)
            intList = soup.find_all(name="int")
            for myInt in intList:
                if myInt.has_attr('name'):
                    if myInt['name'] == "htrc_pageCount":
                        page_count_bin = u.getPageBin(int(myInt.contents[0].string))

            # handle named long elements (not children of arr)
            myLongList = soup.find_all(name="long")
            for myLong in myLongList:
                if myLong.has_attr('name'):
                    if myLong['name'] == "htrc_wordCount":
                        word_count_bin = u.getWordBin(int(myLong.contents[0].string))

            # add unknown value to empty arrays so they can be searched using filters
            if genders == []:
                genders.append("unknown")
            if lc_classes == []:
                lc_classes.append("unknown")
            if lc_subclasses == []:
                lc_subclasses.append("unknown")
            if genres == []:
                genres.append("unknown")
            if languages == []:
                languages.append("unknown")

            searchString = "<a href='http://hdl.handle.net/2027/" + volumeId + "'>" + title + "</a>"

            json.dump(OrderedDict([('date', date),('searchstring', searchString),('lc_classes', lc_classes),('lc_subclass', lc_subclasses),('fiction_nonfiction', fiction_nonfiction),('genres', genres),('languages', languages),('format', form),('is_gov_doc',is_gov_doc),('page_count_bin', page_count_bin),('word_count_bin', word_count_bin),('publication_country', publication_country),('publication_state',publication_state),('publication_place', publication_place),('filename', filename)]), cat)
            cat.write('\n')

    lineNum+=1

cat.close()
hathi.close()
logging.info("done")

