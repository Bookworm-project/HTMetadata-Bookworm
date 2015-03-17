#!/usr/bin/python3

import json
import sys
import re


def main():
    for line in sys.stdin:
        data = json.loads(line)
        title = re.sub(".*'>(.*)</a>.*","\\1",data['searchstring'])
        filename = data['filename']
        writable = "\t".join([filename,title]) + "\n"
        sys.stdout.write(writable)


main()

        

