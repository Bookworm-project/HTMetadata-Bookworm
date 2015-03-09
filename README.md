HTBookwormCatalogGenerator
==================


Reads a hathifiles text file one line at a time, makes calls to HTRC's Solr Proxy API for additional metadata, and creates a catalog file files for use in generating a Bookworm based on HTRC texts.

Usage: python3 generator.py [hathifile hathifile] [--outFile outputDirectory] [--startLine startLine] [--endLine endLine]

Example of advanced usage with piping: head hathifile.txt | python3 generator.py >jsoncatalog.txt.

## arguments:

+ *hathifile* is the filename of the tab-delimited text files containing metadata from HathiTrust, or a stream of Hathifile lines from stdin.
    - downloaded from http://www.hathitrust.org/hathifiles
    - described at http://www.hathitrust.org/hathifiles_description

+ *outFile* is the destination file for the metadata. Defaults to stdout.
    - Bookworm wants it as jsoncatalog.txt.

+ *startLine* is the first line of the hathifile to be processed
    - optional
    - default is the first line of the hathifile

+ *endLine* is the last line of the hathifile to be processed
    - optional
    - default is the last line of the hathifile

## Parallel

Using Gnu parallel, you can run multiple processes asynchronously, with different parts of the Hathifiles. Remember that it's still hitting a single server, so limit --jobs to something reasonable.

e.g. Send 1000 lines at a time to 10 simultaneous jobs.

cat hathifile.txt | parallel -n1000 -j10 python3 generator.py >jsoncatalog.txt
