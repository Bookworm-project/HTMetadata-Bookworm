HTBookwormCatalogGenerator
==================


Reads a hathifiles text file one line at a time, makes calls to HTRC's Solr Proxy API for additional metadata, and creates a catalog file files for use in generating a Bookworm based on HTRC texts.

Usage: python3 generator.py hathifile outDirectory startLine endLine

## arguments:

+ *hathifile* is the filename of the tab-delimited text files containing metadata from HathiTrust
    - downloaded from http://www.hathitrust.org/hathifiles
    - described at http://www.hathitrust.org/hathifiles_description

+ *outDirectory* is the destination directory for the ouput catalog file
    - optional
    - default is the current directory
    - the file name will be jsoncatalog.txt
    - a log file will also be created in the outDirectory

+ *startLine* is the first line of the hathifile to be processed
    - optional
    - default is the first line of the hathifile

+ *endLine* is the last line of the hathifile to be processed
    - optional
    - default is the last line of the hathifile