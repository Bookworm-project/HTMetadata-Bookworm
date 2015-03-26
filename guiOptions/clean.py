import json

def main():
    input_file="example-autogen.json" # Better as arg

    indata = json.load(file(input_file))
    # Dict for writing the updated options
    outdata = indata.copy()
    outdata['ui_components'] = []

    marc_lang = open("MarcLanguageCodes.tsv", "r+")
    lang_codes = dict([tuple(line.strip().split("\t")) for line in marc_lang])

    ui = indata['ui_components']
    for component in ui:
        name = component['name']
        print name
        if name == 'languages':
            print component.keys()
            component['name'] = "Language"
            #for description in component['categorical']['descriptions']:
                #print description
        outdata['ui_components'] += [component]

if __name__ == "__main__":
    main()
