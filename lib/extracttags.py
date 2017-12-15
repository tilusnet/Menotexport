'''Re-structure highlights and notes by grouping by tags.


# Copyright 2016 Guang-zhi XU
#
# This file is distributed under the terms of the
# GPLv3 licence. See the COPYING file for details

Update time: 2016-02-23 23:04:09.
'''


#----------------------------------------
def groupByTags(annodict,verbose=True):
    '''Group highlights and/or notes by tags

    '''
    tags={}

    #----------------Loop through files----------------
    for idii,annoii in annodict.items():

        hlii=annoii.highlights
        ntii=annoii.notes

        if len(hlii)==0 and len(ntii)==0:
            continue

        citeii=annoii.meta['citationkey']
        tagsii=annoii.meta['tags']
        tagsii=['@'+kk for kk in tagsii]

        citedict={'highlights': hlii,\
                  'notes': ntii}

        #----------------Loop through tags----------------
        for tagsjj in tagsii:
            if tagsjj in tags:
                tags[tagsjj][citeii]=citedict
            else:
                tags[tagsjj]={citeii:citedict}

    return tags
