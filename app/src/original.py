from __future__ import print_function
import json
import urllib2

# properties needed to interact with the api
apiToken = //intentionally obfuscated
seToken = //intentionally obfuscated
baseUrl = 'https://www.secretescapes.com/v3'
numberOfRooms = 1
APP_ID = "amzn1.ask.skill.258c1e36-afd4-4d5b-8f50-fbab4ed83475"

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] !=
            APP_ID):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, 
            event['session'])

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

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SearchHolidays":
        return search_holiday(intent, session)
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
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Secret Escapes"
    speech_output = "Welcome to secret escapes, what would you like to search for? or say, inspire me, for some ideas"
    reprompt_text = "say what you would like to search for, or say, inspire me, for some ideas"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_stop_response():
    session_attributes = {}
    card_title = "Secret Escapes"
    speech_output = "Happy travles!"
    reprompt_text = None
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def doCall(urlPath, data):
    if data is None:
        # create GET request 
        req = urllib2.Request(baseUrl + urlPath)
    else:
        # create POST request 
        req = urllib2.Request(baseUrl + urlPath, json.dumps(data))

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
    print("Found " + str(matches) + " matching sale(s)")

    if (matches > 0):
        sale = sales["match"][0]
        return {
            "hotelDetails": sale["title"],
            "location": query,
            "price": str(int(sale["price"]["discounted"])) + " pounds " + sale["price"]["description"]
        }
    return None



def search_holiday(intent, session):

    card_title = "Secret Escapes"
    city = 'Berlin'

    slots = intent['slots']
    if (slots):
        city = slots['city']['value']
        card_title = "Results for " + city

    session_attributes = {"lastresult" : city}
    should_end_session = False
    reprompt_text = None
    result = doSearchQuery(city)

    session_attributes = {       
        "hotelDetails":result["hotelDetails"],
        "location":result["location"],
        "price":result["price"]        
    }
    speech_output = "Sorry, I can't find anything that matches " + city
    if (result):
        speech_output = "How about, " + result['hotelDetails'] + " with prices from " + result['price'] + "?"
        reprompt_text = "Would you like to favourite this, have it sent to you in an email or find something else?"
    return build_response(session_attributes, 
        build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session,
        "directives": [
          {
            "type": "Dialog.ElicitSlot",
            "slotToElicit": "saleAction"
          }
        ]
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


