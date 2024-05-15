'''
This script converts the CSV file output from Discovery Activity logs into a compatible input for use with HomeBank.
'''

import csv
import datetime
import argparse
import re
import os

parser = argparse.ArgumentParser(prog='HomeBank Discover CSV Converter', description='This program takes the CSV file exported from Discover Activity records and converts them into a usable format for import into HomeBank.')
parser.add_argument('-f', '--file', action='store', help='Input file to be used for conversion. The original file is not modified.')
parser.add_argument('-a', '--all', action='store_true', help='Run the tool on all Discover CSV files in either the given directory (using the -d option) or the current directory.')
parser.add_argument('-d', '--directory', help='Enter a directory to be used with the \'-a\' option')
args = parser.parse_args()
discoverInputCSV = []

print('Converter for making Discover CSV files compatible with HomeBank.')

# If the input file is specified directly with the '-f' option, use it.
### Need to clean up the input file path here, for example if the file is .\<input_file>.csv then ".\" gets pulled in and causes pathing issues.
if args.file:
    discoverInputCSV.append(args.file)

# If the '-a' option is used, search for all possible input files. 
elif args.all:
    print('Running converter on all Discover CSV files in the current directory.')
    
    # Search through the current directory and add all Discover CSV files into a list.
    # Grab all of the files by walking the current directory.
    for root, dirs, files in os.walk('.'): 
        allFilesInDirectory = files
        
    # Parse the files and determine which ones fit the Discover CSV criteria
    for file in allFilesInDirectory:
        if re.match('Discover-[a-zA-Z0-9]*-[a-zA-Z0-9()]*[.](csv)', file):
            discoverInputCSV.append(file)

def convert(inputFile):
    # Used to store the needed data between input and output files
    transferList = []
    
    # Append HomeBank_ to the current input file to make it distinct as an output file. 
    discoverOutputCSV = 'HomeBank_' + inputFile
    
    # Open the Discover CSV file
    print('Reading input file {}'.format(inputFile))
    with open(inputFile, newline = '') as csvfileIn:
        reader = csv.DictReader(csvfileIn, delimiter = ',', quotechar = '|')
        
        # store needed information to be written in the new CSV
        # Data needed Post Date -> date, Description -> memo, Amount -> amount
        # All other data is unnecessary or will be added in HomeBank later so can be ignored/left blank when writing
        for row in reader:
            transferList.append(row)

    # Write the new output file with the correct HomeBank format
    print('Writing output file {}'.format(discoverOutputCSV))
    with open(discoverOutputCSV, 'w', newline = '') as csvfileOut:
        # Create the columns in the correct order with all necessary headers: date payment info payee memo amount category tags
        fieldnamesOut = ['date', 'payment', 'info', 'payee', 'memo', 'amount', 'category', 'tags']
        writer = csv.DictWriter(csvfileOut, fieldnames=fieldnamesOut, delimiter = ';', quotechar = '|', quoting = csv.QUOTE_MINIMAL) # delimiter will be between columns
        writer.writeheader()
        
        for row in transferList:
            # Convert the "Post Date" output from Discover to "date" input for HomeBank
            # Format: MM/DD/YYYY -> YYYY-MM-DD
            formattedDate = datetime.datetime.strptime(row.get('Post Date'), '%m/%d/%Y').strftime('%Y-%m-%d')
            writer.writerow({'date': formattedDate, 'memo': row.get('Description'), 'amount': row.get('Amount')})
    
for file in discoverInputCSV:
    convert(file)