from __future__ import print_function
import json
import urllib2
from random import *
from pprint import pprint 
from alexa import *

# Import logger for more detailed debugging tracebacks 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) #<<<<<<<<<<<<<<<<<<<<

def main():

    #open file ./mocks/whatever.json
    # json parse the file

    with open("./mocks/SearchHolidaysIntent.json") as f:
        searchHolidaysData= json.load(f)

    with open("./mocks/InspireMeIntent.json") as f:
        inspireMeData= json.load(f)

    with open("./mocks/FavouriteIntent.json") as f:
        favouriteIntentData= json.load(f)

    with open("./mocks/SkipIntent.json") as f:
        skipIntentData= json.load(f)

    print("========== initial parsing success ==========")

    # catch any errors
    try:
        # if no error, pass the result to lambda_handler function as event in alexa.py
        searchHolidayResults = lambda_handler(searchHolidaysData, searchHolidaysData['context'])
        inspireMeResults = lambda_handler(inspireMeData, inspireMeData['context'])
        favouriteResults = lambda_handler(favouriteIntentData, favouriteIntentData['context'])
        skipIntentResults = lambda_handler(skipIntentData, favouriteIntentData['context']) 

    except Exception as e: 
        # print stacktrace 
        logger.exception("Error occurred when handling the json data")

    # collect result and put result into directory
    writeToJSONFile(searchHolidayResults, inspireMeResults, favouriteResults, skipIntentResults)

# Dumps json data into default output directory (./localTestResults.json)
def writeToJSONFile(searchHolidayResults, inspireMeResults, favouriteResults, skipIntentResults):
    resultsDirectory = './localTestResults.json'
    with open(resultsDirectory, 'w') as fp:
        # combine all json files into one 
        data = { 'searchHolidayResults' : searchHolidayResults, 'inspireMeResults' : inspireMeResults, 'skipIntentResults' : skipIntentResults, 'favouriteResults' : favouriteResults }
        # Add indentation and separators to make json file human readable 
        json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ': '))
        print("========== Results outputted to ./localTestResults.json ==========")

if __name__ == "__main__":
    main()