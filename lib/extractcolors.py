'''


# Copyright 2017 A Szasz
#
# This file is distributed under the terms of the
# GPLv3 licence. See the COPYING file for details

'''
from collections import Counter, OrderedDict


color_labels = OrderedDict([
    ('#fff5ad', 'Yellow'),
    ('#dcffb0', 'Green'),
    ('#bae2ff', 'Blue'),
    ('#d3c2ff', 'Purple'),
    ('#ffc4fb', 'Pink'),
    ('#ffb5b6', 'Red'),
    ('#ffdeb4', 'Orange'),
    ('#dbdbdb', 'Grey')
])


#----------------Get the color of highlights----------------
def getColor(highlights):
    '''Highlights colours are returned as {colour: confidence} pairs
    '''
    colors = Counter([ii['color'] for ii in highlights])
    return {
        color_labels.get(col_code, col_code): cnt * 1. / len(highlights)
        for col_code, cnt in colors.items()
    }

