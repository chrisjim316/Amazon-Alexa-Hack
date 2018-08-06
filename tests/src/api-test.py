import json
import urllib2

## properties needed to interact with the api
apiToken = //intentionally obfuscated
seToken = //intentionally obfuscated
baseUrl = 'https://www.secretescapes.com/v3'
numberOfRooms = 2 
# Search for sale for sales ...

searchData = { 
	"query" : "berlin"
	# , "checkIn" : "2017-12-01"  # optional 
	# , "checkOut" : "2017-12-08"
}


def doCall(urlPath, data):
	if data is None:
		# create GET request 
		req = urllib2.Request(baseUrl + urlPath)
	else:
		# create POST request 
		req = urllib2.Request(baseUrl + urlPath, json.dumps(searchData))

	req.add_header("Content-type", "application/json")
	req.add_header("se-api-token", apiToken)
	req.add_header("se-token", seToken)

	# execute request to get response 
	response = urllib2.urlopen(req).read()

	# all responses are JSON so can be parsed accordingly 
	parsed = json.loads(response)
	return parsed

# Run search call with params specified above
sales = doCall('/search/sales/flash', searchData)

print "Found", len(sales["match"]), "matching sale(s)"
for sale in sales["match"]:
	print sale["id"], "|", sale["title"], "-", sale["reasonToLove"] 
	print "  ", sale["price"]["currency"], sale["price"]["discounted"], sale["price"]["description"]

# assume first sale exists and use it to find offers
saleId = sales["match"][0]["id"]
# sale = doCall('/sales/flash/' + str(saleId), None)

offers = doCall('/sales/flash/' + str(saleId) + '/offers', None)
print "Found", len(offers), "offers for sale:", saleId
# print "\n\n" + json.dumps(offers) + "\n\n"
for offer in offers:
	print "Offer id: ", offer["id"], " Title: ", offer["title"]

# assume first offer exists and use it to check allocations
offerId = offers[0]["id"]
allocations = doCall('/offers/' + str(offerId) + '/allocations?numberOfRooms=' + str(numberOfRooms) + '&departure=', None)

print "Found", len(allocations), "allocations for offer:", offerId
for allocation in allocations:
	print allocation["date"] + ": GBP" + str(allocation["price"])
