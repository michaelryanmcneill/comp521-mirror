from ftplib import FTP
from datetime import datetime
from flask import request, jsonify
import xml.etree.ElementTree as ET
import tempfile
import re
import gzip
from aux_code.httpExceptions import *
from aux_code.dateFunctions import *

def homepage():
    return ("Whoopsie", 400, [])

def pull_trades():
    try:
        input_data = request.get_json()
        startYear = input_data.get('startYear')
        startMonth = input_data.get('startMonth')
        endYear = input_data.get('endYear')
        endMonth = input_data.get('endMonth')
    except Exception:
        return ("Input Error", 400, [])
    
    cik = input_data.get('cik')

    startQuarter = month2quarter(startMonth)
    endQuarter = month2quarter(endMonth)
    indexType = "master"

    #Ensure that you won't run into an infinite loop due to bad input
    errorMsg = isStartBeforeEnd(startYear,startMonth,endYear, endMonth)
    if not (errorMsg == ""):
        return (errorMsg, 400, [])

    year = startYear
    quarter = startQuarter

    ftp = FTP('ftp.sec.gov')
    totalBuys = []
    totalSells = []
    try: 
        ftp.login()
        while (isStartBeforeEnd(year, quarter, endYear, endQuarter) == ""):
            indexDirPath = 'edgar/full-index/'+str(year)+'/QTR'+str(quarter)+'/'+indexType+'.gz'
            binaryIndexFile = pull_edgar_file(ftp, indexDirPath)
            indexFile = ungzip_tempfile(binaryIndexFile)
            edgarFileURLs = parse_idx(indexFile, cik, ['4']) # TODO(valakuzh) allow specification of types of documents
            for url in edgarFileURLs:
                fileTrades = pull_edgar_file(ftp, url)
                xmlTree = parse_section_4(fileTrades)
                trades = return_trade_information_from_xml(xmlTree)
                for trade in trades[0]:
                    if (isStartBeforeEnd(trade['year'],trade['month'],endYear,endMonth) == ""):
                        totalBuys.append(trade)
                for trade in trades[1]:
                    if (isStartBeforeEnd(trade['year'],trade['month'],endYear,endMonth) == ""):
                        totalSells.append(trade)

            #Pull the next index file
            if (quarter<4):
                quarter = quarter + 1
            else:
                year = year + 1
                quarter = 1

    except FivehundredException as e:
        return (e.msg, 504, [])
#    except Exception:
#        return ("Edgar error", 504, [])
    finally:
        ftp.close()
    return jsonify({"buys" : totalBuys, "sells": totalSells})

# Function in order to retrieve an index from the edgar database
# Assumes the ftp channel has been opened already
def pull_edgar_file(ftp, directoryPath):

    pracFile = tempfile.TemporaryFile()
    print directoryPath
    ftp.retrbinary('RETR '+ directoryPath, pracFile.write)
#    try:
#        ftp.retrbinary('RETR '+ directoryPath, pracFile.write)
#    except Exception as e:
#        raise FivehundredException("File not found in Edgar database")
    pracFile.seek(0)
    return pracFile

parse_idx_start = re.compile(r'-+$')
parse_idx_entry = re.compile(r''' ( [0-9]  + )    # CIK
                               \|   [^|]   *      # (skip) name
                               \| ( [^|]   + )    # form type
                               \|   [0-9-] +      # (skip) date
                               \| ( edgar/data/[0-9]+/[0-9-]+\.txt ) # path
                               $ ''', re.VERBOSE)

def ungzip_tempfile(fileobj):
    fileobj.seek(0)
    return gzip.GzipFile("", fileobj=fileobj, mode='r')

def parse_idx(fileobj, target_cik, form_types):
    out = []
    found_start = False
    for line in fileobj:
        if found_start: # i.e., we're looking at real entries now
            m = parse_idx_entry.match(line.strip())
            if not m:
                # we expect to be able to parse every line after the start
                raise Exception("could not parse line from EDGAR idx:", line)
            if int(m.group(1)) == target_cik and m.group(2) in form_types:
                out.append(m.group(3))
        elif parse_idx_start.match(line.strip()):
            found_start = True
    if not found_start:
        raise Exception("could not find start line in EDGAR idx")
    return out

# Parses a file containing text from the edgar database.  Returns a tree containing
# all the information that you need
# N.B. Assumes that the file contains valid xml within <XML> tags  
def parse_section_4(inputFile):
    # Find the beginning of the xml in the file
    while not inputFile.readline().startswith('<XML'):
        pass

    # Start writing these lines into a separate file in order to remove lines at the bottom
    xmlFile = tempfile.TemporaryFile()
    
    while True:
        line = inputFile.readline()
        if line.startswith('</XML'):
            break
        else:
            xmlFile.write(line)
    inputFile.close() 
    # Turn the file into a tree structure
    xmlFile.seek(0)
    tree = ET.parse(xmlFile)
    xmlFile.close()
    return tree

# Parses the tree to gain the information needed to return the proper object
# Right now : only includes non-derivative transactions
def return_trade_information_from_xml(tree):
    buy = []
    sell = []
    for node in tree.iter('nonDerivativeTransaction'):
        try:
            shares = float(node.find('.//transactionShares/value').text)
            date = node.find('.//transactionDate/value').text
            pricePerShare = float(node.find('.//transactionPricePerShare/value').text)
            BuyOrSell = node.find('.//transactionAcquiredDisposedCode/value').text
        except Exception:
            continue    

        # Parse date to get day month and year
        dateElement = datetime.strptime(date,'%Y-%m-%d')

        if (BuyOrSell == 'D'): # Implies sell
            buy.append(dict(number=shares, price=pricePerShare, year=dateElement.year, month=dateElement.month, day=dateElement.day))
        elif (BuyOrSell == 'A'): # Implies buy
            sell.append(dict(number=shares, price=pricePerShare, year=dateElement.year, month=dateElement.month, day=dateElement.day))
    return [buy,sell]