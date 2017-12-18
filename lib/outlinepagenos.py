import string

from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.psparser import PSLiteral
from pdfminer.pdfdocument import PDFNoOutlines
from collections import namedtuple
from bisect import bisect_right

from tools import conv

TocEntry = namedtuple('TocEntry', 'level, title, pageno, parent_index')
ChapterEntry = namedtuple('ChapterEntry', 'level, title, pageno')

class OutlinePagenos:
    """
    Detects and assigns page numbers to PDF table of contents (outlines in PDF parlance).
    """

    def __init__(self, pdfdocument):
        """
        :param pdfdocument: PDFDocument
        """

        self.doc = pdfdocument
        self.msg = []
        pages = dict((page.pageid, pageno) for (pageno, page)
                     in enumerate(PDFPage.create_pages(self.doc)))

        self.toc = [x for x in self._generate_toc(pages)]
        self._populate_toc_parents()
        self.pageno_keys = [x.pageno for x in self.toc]


    def get_chapter(self, pageno, parents=True):
        """
        Return the list of ChapterEntry hierarchy in which this pageno is.
        ChapterEntry is a tuple of (level, title, pageno).
        :param pageno: Lookup this page number. Starting at 1 (human friendly).
        :param parents: if False, return only the innermost ChapterEntry in the hierarchy.
        :return: ([ChapterEntries], ambiguous=boolean). Page numbers start at 1.
        """
        if len(self.toc) == 0:
            # Missing TOC
            return [ChapterEntry(level=1, title="No TOC", pageno=0)], False

        # shifting pageno to zero based, internal repr
        pageno -= 1
        # find the index of the chapter within which pageno is
        try:
            ch_idx = self._find_le(self.pageno_keys, pageno)
        except ValueError:
            # note is before the first TOC entry: label it as [COVER], page 1
            return [ChapterEntry(level=1, title="[COVER]", pageno=1)], False
        # Chapters may start halfway in the page, flag these ambiguities.
        # Only non top level chapters are ambiguous
        ambig = (
            self.pageno_keys[ch_idx] == pageno and
            self.toc[ch_idx].level != 1
        )
        ch_entries = []
        idx = ch_idx
        while idx:
            toc_x = self.toc[idx]
            ch_x = ChapterEntry(level=toc_x.level, title=toc_x.title, pageno=toc_x.pageno+1)
            ch_entries.append(ch_x)
            if not parents:
                break
            idx = toc_x.parent_index
        return ch_entries, ambig

    def print_toc(self, padding_char=' '):
        padding_mult = 2
        for x in self.toc:
            print('{indent}{title}{pageno_padding}{pageno} (->[{parent_index}])'.format(
                indent=' '*padding_mult*x.level,
                title=x.title.encode('utf-8'),
                pageno_padding=padding_char*(80 - x.level*padding_mult - len(x.title) - len(str(x.pageno))),
                pageno=x.pageno + 1,
                parent_index=x.parent_index
            ))

    @staticmethod
    def _find_le(a, x):
        """Find index of rightmost value less than or equal to x"""
        i = bisect_right(a, x)
        if i:
            return i - 1
        raise ValueError


    def _sanitise_title(self, title):
        ret = title.replace('\r', ' ')
        ret = ''.join([c for c in ret if ord(c) >= 32])
        return ret

    def _populate_toc_parents(self):
        latest_level_indices = [None]
        lli = latest_level_indices
        for i, x in enumerate(self.toc):
            if len(lli) > x.level:
                lli[x.level] = i
            else:
                lli.insert(x.level, i)
            self.toc[i] = x._replace(parent_index=lli[x.level - 1])

    def _generate_toc(self, pages):
        try:
            outlines = self.doc.get_outlines()
            for (level, title, dest, a, se) in outlines:
                pageno = None
                try:
                    if dest:
                        dest = self._resolve_dest(dest)
                        if isinstance(dest, dict):
                            dest = dest['D']
                        pageno = pages[dest[0].objid]
                    elif a:
                        action = a
                        if isinstance(action, PDFObjRef):
                            action = self._resolve_dest(action)
                        if isinstance(action, dict):
                            subtype = action.get('S')
                            if subtype and repr(subtype) == '/GoTo' and action.get('D'):
                                dest = self._resolve_dest(action['D'])
                                if isinstance(dest, dict):
                                    dest = dest['D']
                                pageno = pages[dest[0].objid]
                except AttributeError:
                    self.msg.append('My TOC parsing heuristic is not robust enough for this PDF. '
                                     'You may want to improve it.')
                if pageno is not None:
                    title = self._sanitise_title(title)
                    yield TocEntry(level, title, pageno, None)
        except PDFNoOutlines:
            self.msg.append('PDF has no TOC.')

    def _resolve_dest(self, dest):
        if isinstance(dest, str):
            dest = resolve1(self.doc.get_dest(dest))
        elif isinstance(dest, PSLiteral):
            dest = resolve1(self.doc.get_dest(dest.name))
        elif isinstance(dest, PDFObjRef):
            dest = resolve1(dest)
        return dest


class ChapterFormatter:

    def __init__(self):
        self.latest_printed = ([ChapterEntry(0, '', 0)], False)

    def get_formatted_chapter(self, toc_loc, force=False, indent=2):
        if self.latest_printed == toc_loc and not force:
            return ''
        self.latest_printed = toc_loc
        chapters, ambiguous = toc_loc
        outstr = u'''
\n{0}In Chapter{1}:
{2}'''.format(indent*'\t', *map(conv, ['[ambig!]' if ambiguous else '', self._fmt_chapter_hierarchy(chapters, indent)]))
        return outstr

    @staticmethod
    def _fmt_chapter_hierarchy(chapters, indent):
        chapters = sorted(chapters, key=lambda chapter: chapter.level)
        indented_chapter_items = ['%s%s%s (page %d)' % (indent*'\t', ' '*2*c.level, c.title, c.pageno)
                                  for c in chapters]
        return '\n'.join(indented_chapter_items)


class PageFormatter:
    def __init__(self):
        self.latest_printed = -1

    def get_formatted_page(self, page, force=False, indent=3):
        if self.latest_printed == page and not force:
            return ''
        self.latest_printed = page
        return u'''
\n{0}: Page {1}'''.format(indent*'\t', page)

