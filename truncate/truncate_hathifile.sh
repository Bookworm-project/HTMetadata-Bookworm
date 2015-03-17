# These are the commands used to pull out only the relevant parts of a hathifile, corresponding to 
# ids in the dataset being ingesting into bookworm

# Sort hathifile (for fast comparison)
sort hathi_full_20150201.txt >sorted-hathifile.txt

# Pull out ids from Bookworm's unigrams.txt, removing duplicates
cat ../BookwormDB/unigrams.txt | parallel --pipe --block 100M -j23 awk -f remove-consecutive-dupes.awk >NGPD-ids.txt &
sort NGPD-ids.txt | uniq >NGPD-ids-sorted.txt
rm NGPD-ids.txt

# Pull out relevant lines from Hathifile
python select-hathiline.py >truncated-hathifile.txt
