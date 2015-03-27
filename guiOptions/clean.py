import json
import argparse
import sys

def main():

    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFile", nargs="?", help="location of automatically generated options json file", default=sys.stdin)
    args = parser.parse_args()

    indata = json.load(open(args.inputFile, 'r'))
    # Dict for writing the updated options
    outdata = indata.copy()
    outdata['ui_components'] = []

    ui = indata['ui_components']
    for component in ui:
        name = component['name']
        print (name)

        if name == 'lc_class':
            component['name'] = "Class"
        if name == 'lc_subclass':
           component['name'] = "Subclass"
        if name == 'fiction_nonfiction':
            component['name'] = "Fiction/Nonfiction"
        if name == 'genre':
            component['name'] = "Genre"
        if name == 'languages':
            component['name'] = "Language"
        if name == 'format':
            component['name'] = "Format"
        if name == 'is_gov_doc':
            component['name'] = "Government Document"
        if name == 'page_count_bin':
            component['name'] = "Page Count"
        if name == 'word_count_bin':
            component['name'] = "Word Count"
        if name == 'publication_country':
            component['name'] = "Publication Country"
        if name == 'publication_state':
            component['name'] = "Publication State"
        if name == 'date_year':
            component['name'] = "Publication Year"

        outdata['ui_components'] += [component]

if __name__ == "__main__":
    main()
