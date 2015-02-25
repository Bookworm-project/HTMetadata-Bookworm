def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def file_line_count(filename):
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i+1


def getWordBin(wordCount):

    if wordCount is None:
        return "unknown"

    try:
        float(wordCount)
    except ValueError:
        return "unknown"

    if wordCount < 34806:
        return "S - Less than 34806"
    elif wordCount < 91778:
        return "M - Between 34806 and 91778"
    elif wordCount < 185922:
        return "L - Between 91778 and 185921"
    else:
        return "XL - Greater than 185921"


def getPageBin(pageCount):

    if pageCount is None:
        return "unknown"

    try:
        float(pageCount)
    except ValueError:
        return "unknown"

    if pageCount < 150:
        return "S - Less than 150"
    elif pageCount < 350:
        return "M - Between 150 and 350"
    elif pageCount < 551:
        return "L - Between 350 and 550"
    else:
        return "XL - Greater than 550"


