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

solrEndpoint = "http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:"

# set default hathifilename
hathifilename = "hathifile.txt"

# use provided hathifilename if one is provided
if len(sys.argv) > 1:
    hathifilename = sys.argv[1]

# set other defaults
outDir = os.getcwd()
startLine = 0
endLine = u.file_line_count(hathifilename)

# use provided outDir, if one is provided
if len(sys.argv) > 2:
    outDir = sys.argv[2]

# use provided start line, if valid
if len(sys.argv) > 3 and u.is_int(sys.argv[3]) and int(sys.argv[3]) < endLine:
    startLine = int(sys.argv[3])

# use provided end line, if valid
if len(sys.argv) > 4 and u.is_int(sys.argv[4]) and int(sys.argv[4]) < endLine and int(sys.argv[4]) >= startLine :
    endLine = int(sys.argv[4])

ts = time.time()
batchTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d'+'T'+'%H:%M')

lineNum = 1

# log progress
with open(outDir + os.sep + "solr2bookwormCat_log_" + batchTime + ".txt", 'w') as log:
    with open(outDir + os.sep + "jsoncatalog.txt", 'w+') as cat:

        print("startLine: " + str(startLine))
        print("endLine: " + str(endLine))
        log.write("batch time:" + str(batchTime) + "\n")
        log.write("startLine: " + str(startLine) + "\n")
        log.write("endLine: " + str(endLine) + "\n")
        # read in one line at a time, write out one json string at a time, logging progress
        with open(hathifilename) as f:
            for line in f:
                if lineNum >= startLine:

                    print ("reading line number " + str(lineNum) + " ...")
                    log.write("reading line number " + str(lineNum) + "\n")
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

                            elif arr['name'] == "htrc_gender":
                                genderArr = arr.contents
                                for gender in genderArr:
                                    genders.append(gender.string)

                            elif arr['name'] == "country_of_pub":
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

                        searchString = "<a href=\"http://babel.hathitrust.org/cgi/pt?id=" + volumeId + "\" target=\"_blank\">" + title + "</a>"

                        json.dump(OrderedDict([('date', date),('searchstring', searchString),('lc_classes', lc_classes),('lc_subclass', lc_subclasses),('fiction_nonfiction', fiction_nonfiction),('genres', genres),('languages', languages),('format', form),('author_genders', genders),('page_count_bin', page_count_bin),('word_count_bin', word_count_bin),('publication_country', publication_country),('publication_place', publication_place),('filename', filename)]), cat)
                        cat.write('\n')


                lineNum+=1
                if lineNum > endLine:
                    break

print("done")

