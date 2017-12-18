'''


# Copyright 2017 A Szasz
#
# This file is distributed under the terms of the
# GPLv3 licence. See the COPYING file for details

'''
from collections import Counter, OrderedDict
import operator


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


class HighlightColor(dict):
    '''
    Caters for probabilities, hence represented by a dict.
    Colors are displayed in decreasing probability order.
    Probabilities are displayed in percentages w/o decimals.
    '''
    def __str__(self):
        return '{%s}' % ', '.join(
            ['{}: {:.0f}%'.format(k, v * 100)
             for k, v in sorted(self.items(), key=operator.itemgetter(1), reverse=True)
             ]
        )


#----------------Get the color of highlights----------------
def getColor(highlights):
    '''Highlights colours are returned as {colour: confidence} pairs
    '''
    colors = Counter([ii['color'] for ii in highlights])
    hl_color = HighlightColor({
        color_labels.get(col_code, col_code):
            cnt * 1. / len(highlights)
        for col_code, cnt in colors.items()
    })
    return hl_color
