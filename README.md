# pdf_to_searcheable_pdf

A cross-platform python command-line utility that converts any PDF file containing images or unsearcheable fonts to a searcheable text PDF file using tesseract OCR (optical character recognition) and other open source libraries

## Usage

`$ python pdf_to_searchable_pdf.py [-h] [-d DATA_DIR] [-t] [-i] input_filename`

    positional arguments:
        input_filename        input pdf filename

    optional arguments:
    -h, --help            show this help message and exit
    -d DATA_DIR, --data_dir DATA_DIR
                            input data directory
    -t, --text_flag       flag to output text file
    -i, --intermediates_flag
                            flag to output intermediate (page image and pdf) files

## Requirements/Dependencies

* Python 3.6 or up
* Python modules listed in the requirements.txt
* tesseract OCR 
* Poppler (Windows users will have to build or download poppler for Windows: (https://github.com/oschwartz10612/poppler-windows/releases/) which is the most up-to-date. You will then have to add the `bin/` folder to [PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/).

