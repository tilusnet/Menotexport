'''Re-structure highlights and notes by grouping by colors.


# Copyright 2017 A Szasz
#
# This file is distributed under the terms of the
# GPLv3 licence. See the COPYING file for details

'''

import os
from textwrap import TextWrapper

from lib import tools
from tools import printHeader, printInd



#--------------Export annotations grouped by colors------------------
def exportAnno(annodict,outdir,action,verbose=True):
    '''Export annotations grouped by colors
    Uses the vanilla annodict structure, i.e. there's no need 
    to regroup like with extracttags.
    '''

    #-----------Export all to a single file-----------
    if 'm' in action and 'n' not in action:
        fileout='Mendeley_highlights_by_colors.txt'
    elif 'n' in action and 'm' not in action:
        fileout='Mendeley_notes_by_colors.txt'
    elif 'm' in action and 'n' in action:
        fileout='Mendeley_annotations_by_colors.txt'

    abpath_out=os.path.join(outdir,fileout)
    if os.path.isfile(abpath_out):
        os.remove(abpath_out)

    if verbose:
        printHeader('Exporting all annotation colors to:',3)
        printInd(abpath_out,4)

    conv=lambda x:unicode(x)

    wrapper=TextWrapper()
    wrapper.width=70
    wrapper.initial_indent=''
    wrapper.subsequent_indent='\t\t'

    wrapper2=TextWrapper()
    wrapper2.width=60
    wrapper2.initial_indent=''
    wrapper2.subsequent_indent='\t\t\t'

    with open(abpath_out, mode='a') as fout:

        #----------------Loop through sorted citation tags----------------
        for annoii in sorted(annodict.values(), key=lambda d: d.meta['citationkey']):

            outstr=u'''\n\n{0}\n[@{1}]: {2}'''.format(
                int(80)*'-',
                conv(annoii.meta['citationkey']),
                conv(annoii.meta['title'])
            )
            outstr=outstr.encode('ascii','replace')
            fout.write(outstr)

            for color_code, color_name in tools.color_labels.items():
                matching_color_hls = [hl for hl in annoii.highlights if hl.color == color_name]
                matching_color_nts = [nt for nt in annoii.notes if nt.color == color_name]

                # -----------------Write highlights grouped by color-----------------
                if len(matching_color_hls) > 0:
                    outstr = u'''\n\n\t:{0} highlights:'''.format(conv(color_name.upper()))
                    outstr = outstr.encode('ascii', 'replace')
                    fout.write(outstr)

                    for hlii in matching_color_hls:
                        hlstr = wrapper.fill(hlii.text)
                        outstr = u'''
\n\t\t> {0}

\t\t\t- Page: {1}
\t\t\t- Ctime: {2}'''.format(*map(conv, [hlstr, hlii.page, hlii.ctime]))
                        outstr = outstr.encode('ascii', 'replace')
                        fout.write(outstr)

                # -----------------Write notes grouped by colors-----------------
                if len(matching_color_nts) > 0:
                    outstr = u'''\n\n\t:{0} notes:'''.format(conv(color_name.upper()))
                    outstr = outstr.encode('ascii', 'replace')
                    fout.write(outstr)

                    for ntii in matching_color_nts:
                        ntstr = wrapper.fill(ntii.text)
                        outstr = u'''
\n\t\t- {0}

\t\t\t- Page: {1}
\t\t\t- Ctime: {2}'''.format(*map(conv, [ntstr, ntii.page, ntii.ctime]))
                        outstr = outstr.encode('ascii', 'replace')
                        fout.write(outstr)
