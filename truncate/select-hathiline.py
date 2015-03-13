'''
Compare a sorted list of HT ids with lines in a sorted hathifile.

'''
import logging

logging.basicConfig(filename="select.log", level=logging.INFO)

ht = open("sorted-hathifile.txt", "r+")
bw = open("NGPD-ids-sorted.txt")

count = 0
for match in bw:
    match = match.strip()
    logging.debug("Setting match as %s" % match)
    if len(match) == 0:
        continue
    while True:
        l = ht.readline().strip()
        if not l:
            break
        compare = l[:len(match)]

        count += 1
        if count % 100000 == 0:
            logging.info("%d Hathilines read, current match is %s, current hathiline is %s" % (count, match, compare))
        
        if match > compare:
            continue
        elif l.startswith(match):
            print l
            break
        else:
            logging.error("Somehow we missing %s in the Hathifile.")
            break

