'''Extract sticky notes and side-bar notes from documents in Mendeley.


# Copyright 2016 Guang-zhi XU
#
# This file is distributed under the terms of the
# GPLv3 licence. See the LICENSE file for details.
# You may use, distribute and modify this code under the
# terms of the GPLv3 license.

Update time: 2016-04-12 22:09:38.
'''
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from lib.outlinepagenos import OutlinePagenos
import tools


#------------------------Initiate analysis objs------------------------
def init(filename,verbose=True):
    '''Initiate analysis objs
    '''

    fp = open(filename, 'rb')
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    return document


#-----------------Extract notes-----------------
def extractNotes(filename,anno,verbose=True):
    '''Extract notes

    <filename>: str, absolute path to a PDF file.
    <anno>: FileAnno obj, contains annotations in PDF.
    
    Return <nttexts>: list, Anno objs containing annotation info from a PDF.
                      Prepare to be exported to txt files.
    '''
    from extracthl import Anno

    notes=anno.notes
    meta=anno.meta
    nttexts=[]


    #--------------Build outline (toc) structure------
    opn = OutlinePagenos(init(filename))


    #----------------Loop through pages----------------
    if len(anno.ntpages)==0:
        return nttexts

    for pp in anno.ntpages:

        for noteii in notes[pp]:
            note_color=tools.color_labels.get(noteii['color'], noteii['color'])
            textjj=Anno(noteii['content'], ctime=noteii['cdate'],\
                    color=note_color,\
                    title=meta['title'],\
                    page=pp,citationkey=meta['citationkey'], note_author=noteii['author'],\
                    tags=meta['tags'],\
                    toc_loc=opn.get_chapter(pp))
            nttexts.append(textjj)

    return nttexts

