# EasyRide
Calculates the sum of the charged amounts of EasyRide receipts.

Run with
```
usage: calculate_sum.py [-h] [-language {EN}] [-minAmount MINAMOUNT] [-maxAmount MAXAMOUNT] [-startDate STARTDATE]
                        [-endDate ENDDATE] [-weekdays] [-log {40,30,20,10}]
                        [PATH]

positional arguments:
  PATH                  the path where the PDF files with the receipts are located. Default is "."

optional arguments:
  -h, --help            show this help message and exit
  -language {EN}        the language of the receipts
  -minAmount MINAMOUNT  the minimum amount that is considered
  -maxAmount MAXAMOUNT  the maximum amount that is considered
  -startDate STARTDATE  the start date in format YYYY-MM-DD
  -endDate ENDDATE      the end date in format YYYY-MM-DD
  -weekdays             only consider receipts from weekdays (Monday-Friday)
  -log {40,30,20,10}    the logging level (lower means more info)
```

# Examples

1. Sum up all EasyRide receipts in the directory "receipts":
```
python3 calculate_sum.py receipts               
```
results in
```
Total sum: CHF 726.00 (47 entries)
```
2. Sum up all EasyRide receipts larger or equal than CHF 19.90 where the rides took place on a weekday.
```
python3 calculate_sum.py -minAmount 19.90 -weekdays receipts
```
results in
```
Total sum: CHF 517.40 (26 entries)
```
3. Sum up all EasyRide receipts during last Christmas period.
```
python3 calculate_sum.py -startDate 2021-12-24 -endDate 2022-01-02 receipts
```
results in
```
Total sum: CHF 0.00 (0 entries)
```

# Known limitations

At the moment, only receipts in English are supported. To add more languages, additional regular expressions for extracting amounts and dates from the PDF files must be added to the code.
