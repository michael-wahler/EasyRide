from PyPDF2 import PdfFileReader
import re
from os import listdir
from os.path import isfile, join
import argparse
import logging

# This script extracts amount from the automatically generated
# EasyRide receipts from SBB.

# The regular expression in the English version of EasyRide
REGEX = {'EN' : 'Total amount chargedCHF (.+?)VAT'}

FILETYPE = '.pdf'

#
# Searches for "Total amount charged" in page 0 of the PDF, returns amount in CHF
def extract_total_amount (args, regex, filename):
    with open(join(args.path,filename), 'rb') as file:
        pdfReader = PdfFileReader(file)
        pageObj = pdfReader.getPage(0)
        # extracting text from page
        text=pageObj.extractText()
        m = re.search(regex, text)
        if m:
            found = m.group(1)
            return float(found)
        else:
            raise Exception ('no amount could be found')


def process_files (args):
    logging.info ('Searching for files in path {path}...'.format(path=args.path))
    filelist = [f for f in listdir(args.path) if isfile(join(args.path, f))]
    logging.info ('  Processing {n} files.'.format(n=len(filelist)))
    amounts = []
    for file in filelist:
        if (file.endswith(FILETYPE)):
            logging.info ('  Found file of type {filetype}: {filename}'.format(filetype=FILETYPE, filename = file))
            amount = extract_total_amount (args, REGEX[args.language], file)
            logging.info ('  File contains amount {amount}'.format (amount=amount))
            amounts.append(amount)
    calculate_sum(args, amounts)

def calculate_sum (args, amounts):
    logging.info ('Calculating the sum of all amounts...')
    sum = 0.0
    count = 0
    for amount in amounts:
        if (amount >= args.min) and (amount <= args.max):
            logging.info ('  Adding amount CHF {amount}'.format(amount=amount))
            sum += amount
            count += 1
        else:
            logging.info ('  Ignoring amount CHF {amount}'.format(amount=amount))

    print ('Total sum: CHF {sum} ({count} entries)'.format(sum = sum, count=count))


def run_diag (args):
    pass


def main():
    parser = argparse.ArgumentParser(description='Extract amounts from EasyRide purchase receipts and sum them up.')
    parser.add_argument('-p', '--path', default='.', required=False, help='the path where the PDF files with the receipts are located. Default is "."')
    parser.add_argument('-l', '--language', default='EN', choices=['EN'], required=False, help='the language of the receipts')
    parser.add_argument('--min', default=0.0, type=float, required=False, help='the minimum amount that is considered')
    parser.add_argument('--max', default=999999.99, type=float, required=False, help='the maximum amount that is considered')
    parser.add_argument('--loglevel', type=int, default=logging.WARN, choices=[logging.WARN, logging.INFO, logging.DEBUG], help='the logging level (lower means more info)')
    parser.add_argument('-d', '--diag', help='runs some diagnostics (may fail)', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    # if args.diag is None:
    #     process_files (args)
    # else:
    #     run_diag (args)
    process_files (args)

if __name__ == "__main__":
    main()
