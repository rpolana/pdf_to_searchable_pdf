import os, sys
import io
import re
import glob
import argparse
import tempfile

import logging
import configure_logging
log = configure_logging.configure_log(__file__, log_level = 'INFO', log_to_console_flag = True, log_to_file_flag = False)
log.info(f'***Running {sys.argv[0]} with arguments: {sys.argv[1:]}')
log.debug(f'**Current working directory: {os.getcwd()}')
log.debug(f'**Path for loading python modules: {sys.path}')

import pdf_pages_split_merge
pdf_pages_split_merge.configure_log(log)

import pytesseract # Tesseract OCR
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from pdf2image import convert_from_path


MAX_PAGES = -1 # no limit on number of pages
# MAX_PAGES = 100
PAGE_FILENAME_PREFIX = 'page_'
PAGE_FILENAME_PREFIX_SEPARATOR = '_'
PDF_EXTENSION = r'.pdf'
IMAGE_EXTENSION = r'.jpg'
TEXT_EXTENSION = r'.txt'
SEARCHABLE_PDF_SUFFIX = r'_searchable'
PAGE_CONTENT_PREFIX = "*** PAGE "
PAGE_CONTENT_START_SUFFIX = " Start ***\n"
PAGE_CONTENT_END_SUFFIX = " End ***\n"

DATA_DIR_DEFAULT = r'./data'

data_dir = DATA_DIR_DEFAULT
input_filename = r''
intermediates_flag = False
intermediates_dir = data_dir
text_flag = False

# try:
#     type('unicode')
# except:
#     unicode = str

def get_args():
    global input_filename, data_dir, text_flag, intermediates_flag
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", help="input pdf filename", type=str)
    parser.add_argument("-d", "--data_dir", help="input data directory", default=DATA_DIR_DEFAULT)
    # parser.add_argument("-t", "--text_flag", action=argparse.BooleanOptionalAction, help="boolean flag to output text file", default=False)
    parser.add_argument("-t", "--text_flag", action='store_true', help="flag to output text file", default=False)
    parser.add_argument("-i", "--intermediates_flag", action='store_true', help="flag to output intermediate (page image and pdf) files", default=False)
    args = parser.parse_args()
    # print(vars(args))
    # print('\n')
    if args.input_filename is None:
        log.error(f'Please provide an input pdf filename as argument')
        exit(-1)
    else:
        input_filename = args.input_filename
    if args.data_dir:
       data_dir = args.data_dir 
    if args.intermediates_flag:
       intermediates_flag = args.intermediates_flag
    if args.text_flag:
       text_flag = args.text_flag
    return args

def create_searcheable_pdf(input_pdf_filename):
    log.debug(f'input_filename: {input_filename}')
    base_filename = os.path.splitext(os.path.basename(input_filename))[0]
    # base_filename = re.sub(r'(?i)' + PDF_EXTENSION + '\$', '', input_filename.split('/')[-1]) # removes path dirs and PDF extension if any
    log.debug(f'base_filename: {base_filename}')
    pdf_filename = os.path.join(data_dir, base_filename) + PDF_EXTENSION
    # pdf_doc = PdfFileReader(pdf_filename)
    # pages = [pdf_doc.getPage(pg_cntr) for pg_cntr in range(pdf_doc.getNumPages())]
    pages = convert_from_path(pdf_filename)
    log.info(f'Converted {pdf_filename} to {len(pages)} image pages')
    pg_cntr = 1

    intermediates_dir = data_dir
    if not intermediates_flag:
        # temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors = True)
        temp_dir = tempfile.TemporaryDirectory()
        intermediates_dir = temp_dir.name
    if text_flag:
        text_filename = os.path.join(data_dir, base_filename) + TEXT_EXTENSION
    for page in pages:
        if MAX_PAGES < 0 or pg_cntr <= MAX_PAGES:
            log.info(f'Processing image of page {pg_cntr}')
            page_basefilename = PAGE_FILENAME_PREFIX + str(pg_cntr) + PAGE_FILENAME_PREFIX_SEPARATOR + base_filename
            page_image_filename = os.path.join(intermediates_dir, page_basefilename) + IMAGE_EXTENSION
            page.save(page_image_filename)
            log.info(f'Saved image of page {pg_cntr} to {page_image_filename}')
            pdf = pytesseract.image_to_pdf_or_hocr(page_image_filename, extension='pdf')
            if intermediates_flag:
                page_pdf_filename = os.path.join(intermediates_dir, page_basefilename) + PDF_EXTENSION
                with open(page_pdf_filename, 'w+b') as f:
                    f.write(pdf) # pdf type is bytes by default
                    log.info(f'Saved pdf of page {pg_cntr} to {page_pdf_filename}')
            if text_flag:
                with io.open(text_filename, 'a+', encoding='utf8') as f:
                    f.write(PAGE_CONTENT_PREFIX + str(pg_cntr) + PAGE_CONTENT_START_SUFFIX)
                    f.write(str(pytesseract.image_to_string(page_image_filename, timeout=10).encode("utf-8")) +"\n")
                    f.write(PAGE_CONTENT_PREFIX + str(pg_cntr) + PAGE_CONTENT_END_SUFFIX)
                    log.info(f'Appended page {pg_cntr} text to {text_filename}')
            
            # Get bounding box estimates
            # log.info(pytesseract.image_to_boxes(Image.open(page_image_filename)))

            # Get verbose data including boxes, confidences, line and page numbers
            # log.info(pytesseract.image_to_data(Image.open(page_image_filename)))

            # Get information about orientation and script detection
            #log.info(pytesseract.image_to_osd(Image.open(page_image_filename)))

            # log.info(f'OSD information of page {pg_cntr}: \n**')
            # log.info(pytesseract.image_to_osd(page))
            # log.info(f'** end of OSD information of page {pg_cntr}:')

            pg_cntr = pg_cntr + 1
    output_filename = os.path.join(data_dir, base_filename) + SEARCHABLE_PDF_SUFFIX + PDF_EXTENSION
    page_filenames_pattern = os.path.join(intermediates_dir, PAGE_FILENAME_PREFIX + '[0-9]*' + PAGE_FILENAME_PREFIX_SEPARATOR + base_filename + PDF_EXTENSION)
    pdf_pages_split_merge.pdf_merger(page_filenames_pattern, output_filename)
    if not intermediates_flag:
        try:
            intermediates_dir.cleanup()
        except:
            log.warning(f'Errors in cleaning up temporary intermediates directory {intermediates_dir}')


if __name__ == "__main__":
    args = get_args()
    create_searcheable_pdf(input_filename)
    log.info(f'***Finished processing {input_filename}')
    
