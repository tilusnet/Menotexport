'''Export annotations from documents in Mendeley.


# Copyright 2016 Guang-zhi XU
#
# This file is distributed under the terms of the
# GPLv3 licence. See the LICENSE file for details.
# You may use, distribute and modify this code under the
# terms of the GPLv3 license.

Update time: 2016-04-12 22:09:38.
'''

import os
from textwrap import TextWrapper

import lib.extractcolors
from lib.outlinepagenos import ChapterFormatter

from tools import printInd, printNumHeader, printHeader, write_enu, conv



#------------------Export annotations in a single PDF------------------
def _exportAnnoFile(abpath_out,anno,verbose=True):
    '''Export annotations in a single PDF

    <abpath_out>: str, absolute path to output txt file.
    <anno>: list, in the form [file_path, highlight_list, note_list].
            highlight_list and note_list are both lists of
            Anno objs (see extracthl.py), containing highlights
            and notes in TEXT format with metadata. To be distinguished
            with FileAnno objs which contains texts coordinates.
            if highlight_list or note_list is [], no such info
            in this PDF.

    Function takes annotations from <anno> and output to the target txt file
    in the following format:

    -----------------------------------------------------
    # Title of PDF

        > Highlighted text line 1
          Highlighted text line 2
          Highlighted text line 3
          ...
            
            - @citationkey
            - Tags: @tag1, @tag2, @tag3...
            - Ctime: creation time
            - Page: page number (ordinal)
            - Color: highlight color
            - In Chapter: {[ambig!]} Chapter title (p. page number)
    
    -----------------------------------------------------
    # Title of another PDF

        > Highlighted text line 1
          Highlighted text line 2
          Highlighted text line 3
          ...
            
            - @citationkey
            - Tags: @tag1, @tag2, @tag3...
            - Ctime: creation time
            - Page: page number (ordinal)
            - Color: highlight color
            - In Chapter: {[ambig!]} Chapter title (p. page number)

    Use tabs in indention, and markup syntax: ">" for highlights, and "-" for notes.

    Update time: 2016-02-24 13:59:56.
    '''

    conv=lambda x:unicode(x)

    wrapper=TextWrapper()
    wrapper.width=80
    wrapper.initial_indent=''
    #wrapper.subsequent_indent='\t'+int(len('> '))*' '
    wrapper.subsequent_indent='\t'

    wrapper2=TextWrapper()
    wrapper2.width=80-7
    wrapper2.initial_indent=''
    #wrapper2.subsequent_indent='\t\t'+int(len('- Tags: '))*' '
    wrapper2.subsequent_indent='\t\t'

    hlii=anno.highlights
    ntii=anno.notes

    try:
        titleii=hlii[0].title
    except:
        titleii=ntii[0].title

    outstr=u'\n\n{0}\n# {1}'.format(int(80)*'-',conv(titleii))

    with open(abpath_out, mode='a') as fout:
        write_enu(fout, outstr)

        #-----------------Write highlights-----------------
        if len(hlii)>0:

            #-------------Loop through highlights-------------
            for hljj in hlii:
                hlstr=wrapper.fill(hljj.text)
                tagstr=', '.join(['@'+kk for kk in hljj.tags])
                tagstr=wrapper2.fill(tagstr)
                outstr=u'''
\n\t> {0}

\t\t- @{1}
\t\t- Tags: {2}
\t\t- Ctime: {3}
\t\t- Page: {4}
\t\t- Color: {5}
\t\t- In Chapter: {6}{7} (p. {8})
'''.format(*map(conv,[hlstr, hljj.citationkey,\
    tagstr, hljj.ctime, hljj.page, hljj.color,\
    '[ambig!]' if hljj.toc_loc[1] else '', hljj.toc_loc[0][0].title, hljj.toc_loc[0][0].pageno]))
                write_enu(fout, outstr)

        #-----------------Write notes-----------------
        if len(ntii)>0:

            #----------------Loop through notes----------------
            for ntjj in ntii:
                ntstr=wrapper.fill(ntjj.text)
                tagstr=', '.join(['@'+kk for kk in ntjj.tags])
                tagstr=wrapper2.fill(tagstr)
                outstr=u'''
\n\t- {0}

\t\t- @{1}
\t\t- Tags: {2}
\t\t- Ctime: {3}
\t\t- Page: {4}
\t\t- Color: {5}
\t\t- In Chapter: {6}{7} (p. {8})
'''.format(*map(conv,[ntstr, ntjj.citationkey,\
    tagstr, ntjj.ctime, ntjj.page, ntjj.color,\
   '[ambig!]' if ntjj.toc_loc[1] else '', ntjj.toc_loc[0][0].title, ntjj.toc_loc[0][0].pageno]))
                write_enu(fout, outstr)

        

    

    
#--------------------Export highlights and/or notes--------------------
def exportAnno(annodict,outdir,action,separate,verbose=True):
    '''Export highlights and/or notes to txt file

    <annodict>: dict, keys: PDF file paths,
                      values: [highlight_list, note_list], 
                      see doc in _exportAnnoFile().
    <outdir>: str, path to output folder.
    <action>: list, actions from cli arguments.
    <separate>: bool, True: save annotations if each PDF separately.
                      False: save annotations from all PDFs to a single file.

    Calls _exportAnnoFile() for core processes.
    '''

    #-----------Export all to a single file-----------
    if not separate:
            
        if 'm' in action and 'n' not in action:
            fileout='Mendeley_highlights.txt'
        elif 'n' in action and 'm' not in action:
            fileout='Mendeley_notes.txt'
        elif 'm' in action and 'n' in action:
            fileout='Mendeley_annotations.txt'

        abpath_out=os.path.join(outdir,fileout)

        if verbose:
            printInd('Exporting all annotations to:',3)
            printInd(abpath_out,4)

    #----------------Loop through files----------------
    annofaillist=[]

    num=len(annodict)
    docids=annodict.keys()

    for ii,idii in enumerate(docids):

        annoii=annodict[idii]
        fii=annoii.path
        basenameii=os.path.basename(fii)
        fnameii=os.path.splitext(basenameii)[0]

        if verbose:
            printNumHeader('Exporting annos in file',ii+1,num,3)
            printInd(fnameii,4)

        #---------Get individual output if needed---------
        if separate:
            if 'm' in action and 'n' not in action:
                fileout='Highlights_%s.txt' %fnameii
            elif 'n' in action and 'm' not in action:
                fileout='Notes_%s.txt' %fnameii
            elif 'm' in action and 'n' in action:
                fileout='Anno_%s.txt' %fnameii
            abpath_out=os.path.join(outdir,fileout)

            if verbose:
                printInd('Exporting annotations to:',3)
                printInd(abpath_out,4)

        #----------------------Export----------------------
        try:
            _exportAnnoFile(abpath_out,annoii)
        except Exception as e:
            annofaillist.append(basenameii + ':\n' + str(e) )
            continue

    return annofaillist


#--------------Export annotations grouped by tags------------------
def exportAnnoByTags(annodict, outdir, action, verbose=True):
    '''Export annotations grouped by tags

    '''

    #-----------Export all to a single file-----------
    if 'm' in action and 'n' not in action:
        fileout='Mendeley_highlights_by_tags.txt'
    elif 'n' in action and 'm' not in action:
        fileout='Mendeley_notes_by_tags.txt'
    elif 'm' in action and 'n' in action:
        fileout='Mendeley_annotations_by_tags.txt'

    abpath_out=os.path.join(outdir,fileout)
    if os.path.isfile(abpath_out):
        os.remove(abpath_out)

    if verbose:
        printHeader('Exporting all tagged annotations to:',3)
        printInd(abpath_out,4)

    conv=lambda x:unicode(x)

    wrapper=TextWrapper()
    wrapper.width=70
    wrapper.initial_indent=''
    #wrapper.subsequent_indent='\t\t'+int(len('> '))*' '
    wrapper.subsequent_indent='\t\t'

    wrapper2=TextWrapper()
    wrapper2.width=60
    wrapper2.initial_indent=''
    #wrapper2.subsequent_indent='\t\t\t'+int(len('Title: '))*' '
    wrapper2.subsequent_indent='\t\t\t'

    with open(abpath_out, mode='a') as fout:

        #----------------Loop through tags----------------
        tags=annodict.keys()
        if len(tags)==0:
            return
        tags.sort()
        #---------------Put @None at the end---------------
        if '@None' in tags:
            tags.remove('@None')
            tags.append('@None')

        for tagii in tags:

            citedictii=annodict[tagii]
            outstr=u'''\n\n{0}\n# {1}'''.format(int(80)*'-', conv(tagii))
            outstr=outstr.encode('ascii','replace')
            fout.write(outstr)

            #--------------Loop through cite keys--------------
            for citejj, annosjj in citedictii.items():
                hljj=annosjj['highlights']
                ntjj=annosjj['notes']

                outstr=u'''\n\n\t@{0}:'''.format(conv(citejj))
                outstr=outstr.encode('ascii','replace')
                fout.write(outstr)

                #-----------------Write highlights-----------------
                if len(hljj)>0:

                    #-------------Loop through highlights-------------
                    for hlkk in hljj:
                        hlstr=wrapper.fill(hlkk.text)
                        title=wrapper2.fill(hlkk.title)
                        outstr=u'''
\n\t\t> {0}

\t\t\t- Title: {1}
\t\t\t- Ctime: {2}'''.format(*map(conv,[hlstr, title,\
                      hlkk.ctime]))

                        outstr=outstr.encode('ascii','replace')
                        fout.write(outstr)

                #-----------------Write notes-----------------
                if len(ntjj)>0:

                    #----------------Loop through notes----------------
                    for ntkk in ntjj:
                        ntstr=wrapper.fill(ntkk.text)
                        title=wrapper2.fill(ntkk.title)
                        outstr=u'''
\n\t\t- {0}

\t\t\t- Title: {1}
\t\t\t- Ctime: {2}'''.format(*map(conv,[ntstr, title,\
                    ntkk.ctime]))

                        outstr=outstr.encode('ascii','replace')
                        fout.write(outstr)




#--------------Export annotations grouped by colors------------------
def exportAnnoByColors(annodict, outdir, action, verbose=True):
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

    wrapper=TextWrapper(width=55, initial_indent='', subsequent_indent='\t\t\t')

    with open(abpath_out, mode='a') as fout:

        #----------------Loop through sorted citation tags----------------
        for annoii in sorted(annodict.values(), key=lambda d: d.meta['citationkey']):

            outstr=u'''\n\n{0}\n[@{1}]: {2}'''.format(
                int(80)*'-',
                conv(annoii.meta['citationkey']),
                conv(annoii.meta['title'])
            )
            write_enu(fout, outstr)

            for color_code, color_name in lib.extractcolors.color_labels.items():
                matching_color_hls = [hl for hl in annoii.highlights if color_name in hl.color.keys()]
                matching_color_nts = [nt for nt in annoii.notes if nt.color == color_name]

                # -----------------Write highlights grouped by color-----------------
                if len(matching_color_hls) > 0:
                    outstr = u'''\n\n\t:{0} highlights:'''.format(conv(color_name.upper()))
                    write_enu(fout, outstr)
                    ch_fmtr = ChapterFormatter()
                    for hlii in matching_color_hls:
                        outstr = ch_fmtr.get_formatted_chapter(hlii.toc_loc)
                        write_enu(fout, outstr)
                        hlstr = wrapper.fill(hlii.text)
                        outstr = u'''
\n\t\t\t> {0}

\t\t\t\t- Page: {1}
\t\t\t\t- Updates on page: {2}'''.format(*map(conv, [hlstr, hlii.page, hlii.ctime]))
                        write_enu(fout, outstr)
                        color_confidence = hlii.color[color_name]
                        if color_confidence < 1:
                            outstr=u'''
\t\t\t\t- Color confidence: {:.0f}%'''.format(color_confidence*100)
                            write_enu(fout, outstr)

                # -----------------Write notes grouped by colors-----------------
                if len(matching_color_nts) > 0:
                    outstr = u'''\n\n\t:{0} notes:'''.format(conv(color_name.upper()))
                    write_enu(fout, outstr)
                    ch_fmtr = ChapterFormatter()
                    for ntii in matching_color_nts:
                        outstr = ch_fmtr.get_formatted_chapter(ntii.toc_loc)
                        write_enu(fout, outstr)
                        ntstr = wrapper.fill(ntii.text)
                        outstr = u'''
\n\t\t\t- {0}

\t\t\t\t- Page: {1}
\t\t\t\t- Note updated: {2}'''.format(*map(conv, [ntstr, ntii.page, ntii.ctime]))
                        write_enu(fout, outstr)