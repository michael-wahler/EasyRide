from PyPDF2 import PdfFileReader
import re
from os import listdir
from os.path import isfile, join
import argparse
import logging
from datetime import datetime, date

# This script extracts amount from the automatically generated
# EasyRide receipts from SBB.

# List of supported languages
SUPPORTED_LANGUAGES = ['EN']
# The regular expression in the English version of EasyRide for the amount
REGEX_TOTAL_AMOUNT = {'EN' : 'Total amount chargedCHF (.+?)VAT'}
# The regular expression in the English version of EasyRide for the date
REGEX_RIDE_DATE = {'EN' : 'Date: (.+?)Sales-ID'}

# check if all Regexes for the supported languages are defined
# (make this file by adding a language 'XY' to SUPPORTED_LANGUAGES)
for lang in SUPPORTED_LANGUAGES:
    try:
        REGEX_TOTAL_AMOUNT[lang]
        REGEX_RIDE_DATE[lang]
    except KeyError as e:
        print ('INTERNAL ERROR: The source file claims that language {lang} is supported, but it does not define the required regular expressions.'.format(lang=e))
        exit(1)

FILETYPE = '.pdf'
DEFAULT_MIN_AMOUNT = 0.0
DEFAULT_MAX_AMOUNT = 999999.99


# takes as argument the raw text of the PDF
# returns the date of the ride as datetime object
def extract_date_of_ride (args, text):
    m = re.search(REGEX_RIDE_DATE[args.language], text)
    if m:
        found = m.group(1)
        thedate = datetime.strptime(found, '%d %b %Y')
        return thedate
    else:
        return None

# takes as argument the raw text of the PDF
# returns the amount of the ride as a float
def extract_amount_of_ride_in_cents (args, text):
    m = re.search(REGEX_TOTAL_AMOUNT[args.language], text)
    if m:
        found = m.group(1)
        return round (float(found)*100)
    else:
        return None

# returns a string with the raw text of the PDF
def extract_PDF_text (args, filename, pagenumber = 0):
    with open(join(args.path,filename), 'rb') as file:
        pdfReader = PdfFileReader(file)
        pageObj = pdfReader.getPage(pagenumber)
        # extracting text from page
        return pageObj.extractText()

# calculates the sum in the list 'amounts' for each amount between min and max
# returns a tuple of (sum, number of elements that matched criteria)
def calculate_and_print_sum (args, amounts):
    logging.info ('Calculating the sum of all amounts...')
    sum = 0
    count = 0
    for amount in amounts:
        if (amount >= args.minAmount * 100) and (amount <= args.maxAmount * 100):
            logging.info ('  Adding amount CHF (cents) {amount}'.format(amount=amount))
            sum += amount
            count += 1
        else:
            logging.info ('  Ignoring amount CHF (cents) {amount}'.format(amount=amount))

    return [sum, count]

# returns true if the -wd parameter is false (all days are considered) OR
#              if the -wd paramater is true (only weekdays) and the date is between Monday and Friday
def is_day_of_week (args, date):
    if not args.weekdays:
        return True
    else:
        return date.weekday() <= 4


# Goes through all PDFs in the desired directory, extracts amounts, and calculates the sum
def print_total_sum_from_files (args):
    logging.info ('Searching for files in path {path}...'.format(path=args.path))
    filelist = [f for f in listdir(args.path) if isfile(join(args.path, f))]
    logging.info ('  Processing {n} files.'.format(n=len(filelist)))
    amounts = []
    earliest_receipt_found = datetime.now()
    latest_receipt_found = datetime.strptime('01 Jan 1970', '%d %b %Y')

    for file in filelist:
        if (file.endswith(FILETYPE)):
            logging.info ('  Found file of type {filetype}: {filename}'.format(filetype=FILETYPE, filename = file))
            pdf_text = extract_PDF_text(args, file)
            amount = extract_amount_of_ride_in_cents (args, pdf_text)
            date_of_receipt = extract_date_of_ride (args, pdf_text)
            if date_of_receipt < earliest_receipt_found:
                earliest_receipt_found = date_of_receipt
            if date_of_receipt > latest_receipt_found:
                latest_receipt_found = date_of_receipt
            logging.info ('  File contains amount CHF (cents) {amount}'.format (amount=amount))
            # check if date_of_receipt is within the bounds given as arguments
            if (date_of_receipt >= args.startDate) and \
               (date_of_receipt <= args.endDate) and \
               (is_day_of_week(args, date_of_receipt)):
                amounts.append(amount)
    result = calculate_and_print_sum(args, amounts)
    print ('Total sum: CHF {sum:.2f} ({count} entries)'.format(sum = result[0]/100, count=result[1]))
    logging.info ('Earliest receipt found: ' + earliest_receipt_found.strftime('%d %b %Y'))
    logging.info ('Latest receipt found  : ' + latest_receipt_found.strftime('%d %b %Y'))

# this is some code to test new functionality
def run_diag (args):
    logging.info ('Running some diagnostics...')
    filelist = [f for f in listdir(args.path) if isfile(join(args.path, f))]
    if len (filelist) > 0:
        filename = filelist[0]
        if (filename.endswith(FILETYPE)):
            with open(join(args.path,filename), 'rb') as file:
                print (filename)
                pdfReader = PdfFileReader(file)
                pageObj = pdfReader.getPage(0)
                # extracting text from page
                text=pageObj.extractText()
                extract_date_of_ride (args, text)

def main():
    parser = argparse.ArgumentParser(description='Extract amounts from EasyRide purchase receipts and sum them up.')
    parser.add_argument('path', metavar='PATH', default='.', nargs='?', help='the path where the PDF files with the receipts are located. Default is "."')
    parser.add_argument('-language', default='EN', choices=SUPPORTED_LANGUAGES, required=False, help='the language of the receipts')
    parser.add_argument('-minAmount', default=DEFAULT_MIN_AMOUNT, type=float, required=False, help='the minimum amount that is considered')
    parser.add_argument('-maxAmount', default=DEFAULT_MAX_AMOUNT, type=float, required=False, help='the maximum amount that is considered')
    parser.add_argument('-startDate', default='1970-01-01', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), required=False, help='the start date in format YYYY-MM-DD')
    parser.add_argument('-endDate', default=datetime.now().strftime('%Y-%m-%d'), type=lambda s: datetime.strptime(s, '%Y-%m-%d'), required=False, help='the end date in format YYYY-MM-DD')
    parser.add_argument('-weekdays', help='only consider receipts from weekdays (Monday-Friday)', action='store_true')
    parser.add_argument('-log', type=int, default=logging.WARN, choices=[logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG], help='the logging level (lower means more info)')
    parser.add_argument('-diag', help='runs some diagnostics (may fail)', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=args.log)

    if not args.diag:
        print_total_sum_from_files (args)
    else:
        run_diag (args)

if __name__ == "__main__":
    main()
