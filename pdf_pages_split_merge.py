"""pdf_pages_split_merge: 
Functions to split and merge pdf files using pypdf2 module
    Requirements:
        Split: split single pdf file into individual page pdf files
        Merge: merge collection of pdf files based on a pattern into single pdf file, in the order of their name
"""

import os
import glob

import configure_logging
log = configure_logging.get_application_logger()

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger

PDF_EXTENSION = r'.pdf'

def pdf_splitter(pdf_filename, page_dir, max_pages = -1):
    log.info('Splitting {} into pages..'.format(pdf_filename))
    basename = os.path.splitext(os.path.basename(pdf_filename))[0]
    pdf = PdfFileReader(pdf_filename)
    for pg_cntr in range(pdf.getNumPages()):
        if max_pages < 0 or pg_cntr <= max_pages:
            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(pdf.getPage(pg_cntr))
            output_filename = os.path.join(page_dir, ('{}_page_{}'+PDF_EXTENSION).format(basename, pg_cntr+1))
            with open(output_filename, 'wb') as out:
                pdf_writer.write(out)
            log.info('Created page: {}'.format(output_filename))


def pdf_merger(page_filenames_wildcard_pattern, output_filename):
    log.info(f'pdf_merger: page filenames pattern: {page_filenames_wildcard_pattern}')
    page_pdf_filenames = glob.glob(page_filenames_wildcard_pattern)
    page_pdf_filenames.sort()
    log.info(f'pdf_merger: merging pdf filenames: {page_pdf_filenames}')
    pdf_merger = PdfFileMerger()
    for filename in page_pdf_filenames:
        pdf_merger.append(filename)
    with open(output_filename, 'wb') as fh:
        pdf_merger.write(fh)
        log.info(f'pdf_merger: written searchable filename: {output_filename}')
    
    # pg_cntr = 1
    # pdf_writer = PdfFileWriter()
    # for filename in page_pdf_filenames:
    #     if MAX_PAGES < 0 or pg_cntr <= MAX_PAGES:
    #         pdf_reader = PdfFileReader(filename)
    #         for page in range(pdf_reader.getNumPages()):
    #             pdf_writer.addPage(pdf_reader.getPage(page))
    #     pg_cntr += 1
    # with open(output_filename, 'wb') as fh:
    #     pdf_writer.write(fh)
    #     log.info(f'pdf_merger: written searchable filename: {output_filename}')

