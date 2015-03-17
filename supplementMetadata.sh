#! /bin/bash


mkdir -p supplements

bookwormdir=catalogworm

perl -e 'print "date_year\tdecade\n" ; for my $year (1400..2020) {print $year . "\t" . int($year/10)*10 . "\n" }' > supplements/decadeLookup.txt

cd $bookwormdir;

python OneClick.py supplementMetadataFromTSV ../supplements/decadeLookup.txt


