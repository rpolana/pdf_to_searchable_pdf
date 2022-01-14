import os, sys
import io
import re
import glob
import argparse
import tempfile

import logging
import configure_logging
log = configure_logging.configure_log(__file__, log_level = 'DEBUG', log_to_console_flag = True, log_to_file_flag = False)

# try:
#     from PIL import Image
# except:
#     import Image
import pytesseract # Tesseract OCR

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import cv2


MAX_PAGES = -1 # no limit on number of pages
# MAX_PAGES = 100
PAGE_FILENAME_PREFIX = 'page_'
PDF_EXTENSION = r'.pdf'
IMAGE_EXTENSION = r'.jpg'
TEXT_EXTENSION = r'.txt'
SEARCHABLE_PDF_SUFFIX = r'_searchable'

DATA_DIR_DEFAULT = r'./data'

data_dir = DATA_DIR_DEFAULT
input_filename = r''
# input_filename = 'EncryptedPDF'
intermediates_flag = False
intermediates_dir = data_dir
text_flag = False

try:
    type('unicode')
except:
    unicode = str

def get_args():
    global input_filename, data_dir, text_flag, intermediates_flag
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", help="input pdf filename", type=str)
    parser.add_argument("-d", "--data_dir", help="input data directory", default=DATA_DIR_DEFAULT)
    # parser.add_argument("-t", "--text_flag", action=argparse.BooleanOptionalAction, help="boolean flag to output text file", default=False)
    parser.add_argument("-t", "--text_flag", action='store_true', help="flag to output text file", default=False)
    parser.add_argument("-i", "--intermediates_flag", action='store_true', help="flag to output intermediate (page image and pdf) files", default=False)
    args = parser.parse_args()
    print(vars(args))
    print('\n')
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

def ocr_from_image_file(input_filename):
    # By default OpenCV stores images in BGR format and since pytesseract assumes RGB format,
    # we need to convert from BGR to RGB format/mode:
    img_cv = cv2.imread(os.path.join(data_dir, input_filename) + IMAGE_EXTENSION)    
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    log.info(pytesseract.image_to_string(img_rgb))


def ocr_from_bytes(img_cv):
    img_rgb = Image.frombytes('RGB', img_cv.shape[:2], img_cv, 'raw', 'BGR', 0, 0)
    log.info(pytesseract.image_to_string(img_rgb))    


def pdf_splitter(pdf_filename):
    log.info('Splitting {} into pages..'.format(pdf_filename))
    basename = os.path.splitext(os.path.basename(pdf_filename))[0]
    pdf = PdfFileReader(pdf_filename)
    for pg_cntr in range(pdf.getNumPages()):
        if MAX_PAGES < 0 or pg_cntr <= MAX_PAGES:
            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(pdf.getPage(pg_cntr))
            output_filename = os.path.join(intermediates_dir, ('{}_page_{}'+PDF_EXTENSION).format(basename, pg_cntr+1))
            with open(output_filename, 'wb') as out:
                pdf_writer.write(out)
            log.info('Created page: {}'.format(output_filename))


def pdf_merger(output_filename, input_root_filename):
    log.info(f'pdf_merger: input root filename: {input_root_filename}')
    page_pdf_filenames = glob.glob(os.path.join(intermediates_dir, '*_' + input_root_filename + PDF_EXTENSION))
    page_pdf_filenames.sort()
    log.info(f'pdf_merger: merging pdf filenames: {page_pdf_filenames}')
    pdf_merger = PdfFileMerger()
    file_handles = []
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

if __name__ == "__main__":
    log.info(f'Current working directory: {os.getcwd()}')
    log.info(f'Executing python script {__file__}')
    log.info(f'Running {sys.argv}')
    args = get_args()
    ocr_from_pdf_file(input_filename)
    
    # ocr_from_image_file(input_filename)
    
    # img_cv = cv2.imread(os.path.join(data_dir, input_filename) + IMAGE_EXTENSION)    
    # ocr_from_bytes(img_cv)
