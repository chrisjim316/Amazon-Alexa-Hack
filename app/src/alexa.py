from __future__ import print_function
import json
import urllib2
from random import *

# properties needed to interact with the api
apiToken = //intentionally obfuscated
seToken = //intentionally obfuscated
baseUrl = 'https://www.secretescapes.com/v3'
numberOfRooms = 1
APP_ID = "amzn1.ask.skill.258c1e36-afd4-4d5b-8f50-fbab4ed83475"
# this value needs to be persistent,
lastResult = {}
holidayResultsIndex = 0

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] !=
            APP_ID):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    # if  event['session']['attributes']['lastResult'] is not None :      
    #     lastResult = event['session']['attributes']['lastResult']

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    # print("on_intent requestId=" + intent_request['requestId'] +
    #       ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SearchHolidays":
        return search_holiday(intent, session)
    elif intent_name == "InspireMe":
        return inspire_me(intent, session)
    elif intent_name == "Favourite":
        return save_to_fave(intent, session)
    elif intent_name == "Skip":
        return skip(intent, session, holidayResultsIndex)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent":
        return get_stop_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    lastResult = {}
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    speechlet = Speechlet(
        "Welcome to secret escapes, what would you like to search for? or say, inspire me, for some ideas.",
        "saleAction", "say what you would like to search for, or say, inspire me, for some ideas", False)
    return build_response(session_attributes, build_speechlet_response(speechlet))

def get_stop_response():
    session_attributes = {}
    lastResult = {}
    speechlet = Speechlet("Happy travels!", "saleAction", None, True)
    return build_response(session_attributes, build_speechlet_response(speechlet))

def doCall(urlPath, data):
    if data: 
        # create POST request 
        req = urllib2.Request(baseUrl + urlPath, json.dumps(data))
    else:
        # create GET request 
        req = urllib2.Request(baseUrl + urlPath)

    req.add_header("Content-type", "application/json")
    req.add_header("se-api-token", apiToken)
    req.add_header("se-token", seToken)

    # execute request to get response 
    response = urllib2.urlopen(req).read()

    # all responses are JSON so can be parsed accordingly 
    parsed = json.loads(response)
    return parsed

def doSearchQuery(query):
    # Search for sale for sales ...
    searchData = { 
        "query" : query
    }

    # Run search call with params specified above
    sales = doCall('/search/sales/flash', searchData)

    matches = len(sales["match"])

    # print("Found " + str(matches) + " matching sale(s)")

    if (matches > 0):
        sale = sales["match"][0]
        return {
            "saleId":sale["id"],
            "hotelDetails": sale["title"],
            "location": query,
            "price": str(int(sale["price"]["discounted"])) + " pounds " + sale["price"]["description"]
        }
    return None

# doSearchQuery gets the first sale, this returns the entire json array 
def getAllSearchQueries(query): 
    # Search for sale for sales ...
    searchData = { 
        "query" : query
    }

    # Run search call with params specified above
    sales = doCall('/search/sales/flash', searchData)

    matches = len(sales["match"])

    print("Found " + str(matches) + " matching sale(s)")

    return sales["match"]

def addToFave(sale):
    output = "This " + sale["hotelDetails"] + " has been added to your favourites"
    # if not hasFave(sale):
    #     query = {
    #         "saleId":saleId["id"],
    #         "isFavorite":"true"
    #     }
    #     resp = doCall("/my-favourites",query) # figure out the api call
    #     # check if response contains the fave 
    # else:
    #     output = lastResult["hotelDetails"] + " is already in your favourites list"       
    return output

# def hasFave(sale):
#     favourites = doCall('/my-favourites', "")
#     print_json(favourites)

#     _hasFave = False
#     for fave in favourites:
#         if fave["saleId"] is saleId["id"]:
#             _hasFave =True
#     return _hasFave

def search_holiday(intent, session):
    lastResult = {}
    holidayResultsIndex = 0

    city = 'Berlin'
    speechlet = Speechlet(None,"saleAction",None,False)
    slots = intent['slots']
    if (slots):
        city = slots['city']['value']
        speechlet.title ="Results for " + city

    result = doSearchQuery(city)
    session_attributes = {"lastResult" : 
        {
            "saleId":result["saleId"],
            "hotelDetails":result["hotelDetails"],
            "location":result["location"],
            "price":result["price"]
        }
    }

    speech_output = "Sorry, I can't find anything that matches " + city
    if (result):
        speech_output ="How about, " + result['hotelDetails'] + " with prices from " + result['price'] + "?"
        speechlet.addOutput(speech_output)
        speechlet.addReprompt("Would you like to favourite this, have it sent to you in an email or find something else?")
    return build_response(session_attributes, build_speechlet_response(speechlet))

def inspire_me(intent, session):
    speechlet = Speechlet(None,"userActions",None,False)
    session_attributes = {}
    city = "Barcelona"
    slots = intent['slots']
    if (slots):
        speechlet.title ="Results that Inspire me"

    if "attributes" in session:
        session_attributes = {"lastResult" : session['attributes']}
        city = session['attributes']['location']



    result = doSearchQuery(city) 
    session_attributes = {"lastResult" : 
        {
            "saleId":result["saleId"],
            "hotelDetails":result["hotelDetails"],
            "location":result["location"],
            "price":result["price"]
        }
    }
    speech_output = "Sorry, I can't find anything inspiring right now"
    if (result):
        speech_output = "How about, " + result['hotelDetails'] + " with prices from " + result['price'] + "?"
        speechlet .addOutput(speech_output)
        speechlet .addReprompt("Would you like to favourite this, have it sent to you in an email or find something else?")
    return build_response(session_attributes, build_speechlet_response(speechlet ))


# Skip method not done yet, should get sales['match'] and loop by index 
def skip(intent, session, holidayResultsIndex):
    attributes = {}
    speechlet = Speechlet(None,"saleAction",None,False)
    slots = intent['slots']
    if (slots):
        speechlet.title = "Skipping to the next result"
    speech_output = "Sorry, there are no other results that match your query, please try searching for another location"

    # Get test data "city" from SkipIntent.json 
    city = session['attributes']['location']
    holidayResults = getAllSearchQueries(city)

    if (holidayResults):
        # Check if this is a new user session to determine the index 
        if (session['new']):
            holidayResultsIndex = 0
        else:
            # CHANGE THIS INDEX TO CHECK IF SKIP IS WORKING, working as of July 13th, 2018
            holidayResultsIndex += 1
        
        sale = holidayResults[holidayResultsIndex]
        # debugging
        print_json(sale) 
        
        # sometimes json sub-attributes are "id" instead of "saleId", use print_json to check and correct the errors, etc. print_json(sale)
        session_attributes = {
            "saleId":sale["id"],
            "hotelDetails": sale["hotelDetails"],
            "location": sale["location"]["city"]["name"],
            "price": sale["price"]["discounted"]
        }

        speech_output = "How about a hotel at " + sale["location"]["city"]["name"] + " with prices from " + str(sale["price"]["discounted"]) + " pounds per night?"
        speechlet.addOutput(speech_output)
        speechlet.addReprompt("Would you like to favourite this, have it sent to you in an email or find something else? Or would you like other choices?")
    return build_response(session_attributes, build_speechlet_response(speechlet))

def save_to_fave(intent,session):
    speechlet = Speechlet(None,"saleAction",None,False)

    # Get test data from FavouriteIntent.json and append it to lastResult
    lastResult = session['attributes']

    session_attributes = {"lastResult" : lastResult}

    output = "Sorry, there is no destination to put into your favourites. I can try to search for a holiday or I could try and inspire you with some ideas"
    if lastResult:
        addToFave(lastResult)
        output = "I have successfully favourited the " + lastResult['location'] + " sale"
    speechlet.addOutput(output)
    return build_response(session_attributes,build_speechlet_response(speechlet))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(speechlet):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': speechlet.getOutput()
        },
        'card': {
            'type': 'Simple',
            'title': speechlet.title,
            'content': speechlet.getOutput()
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speechlet.getReprompt()
            }
        },
        'shouldEndSession': speechlet.should_end_session,
        "directives": [
          {
            "type": "Dialog.ElicitSlot",
            "slotToElicit": speechlet.slot
          }
        ]
    }


# def build_speechlet_response(title, output, reprompt_text, should_end_session):
#     return {
#         'outputSpeech': {
#             'type': 'PlainText',
#             'text': output
#         },
#         'card': {
#             'type': 'Simple',
#             'title': title,
#             'content': output
#         },
#         'reprompt': {
#             'outputSpeech': {
#                 'type': 'PlainText',
#                 'text': reprompt_text
#             }
#         },
#         'shouldEndSession': should_end_session,
#         "directives": [
#           {
#             "type": "Dialog.ElicitSlot",
#             "slotToElicit": "saleAction"
#           }
#         ]
#     }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# Print contents of json file 
def print_json(jsonToBeDebugged):
    resultsDirectory = './localJsonDebuggingOutput.json'
    with open(resultsDirectory, 'w') as fp:
            # combine all json files into one 
            data = { 'jsonDebugOutput' : jsonToBeDebugged }
            # Add indentation and separators to make json file human readable 
            json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ': '))
            print("========== Results outputted to ./localJsonDebuggingOutput.json ==========")


class Speechlet:

    def __init__(self,output,slot,reprompt,is_end_session):
        self.title= "Secret Escapes"
        self.outputs = []
        if output is not None:
            self.outputs.append(output)
        self.slot = slot
        self.reprompts = []
        if reprompt is not None:
            self.reprompts.append(reprompt)
        self.should_end_session = is_end_session

    def getOutput(self):
        if(len(self.outputs) >0):
            # pick random
            return self.outputs[self.pickRandom(self.outputs)]
        else:
            return None

    def getReprompt(self):
        if(len(self.reprompts) >0):
            # pick random
            return self.reprompts[self.pickRandom(self.reprompts)]
        else:
            return None

    def pickRandom(self,list):
        return randint(0,len(list)-1)

    def addOutput(self,output):
        # check if it extists to not add duplicates
        if output not in self.outputs:
            self.outputs.append(output)

    def addReprompt(self,reprompt):
        if reprompt not in self.reprompts:
            self.reprompts.append(reprompt)

    def removeOutput(self,output):
        if output in self.outputs:
            self.outputs.remove(output)

    def removeReprompt(self,reprompt):
        if reprompt in self.reprompts:
            self.reprompts.remove(reprompt)
