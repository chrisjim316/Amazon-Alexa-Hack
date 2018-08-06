import json
import urllib2

## properties needed to interact with the api
apiToken = //intentionally obfuscated
baseUrl = 'https://www.secretescapes.com/v3'
userEmail = //intentionally obfuscated
userPassword = //intentionally obfuscated

# login with a users email and password ...

req = urllib2.Request(baseUrl + '/user/signin')
req.add_header("Content-type", "application/json")
req.add_header("se-api-token", apiToken)

data = {
	"email": userEmail,
    "password": userPassword
}

response = urllib2.urlopen(req, json.dumps(data)).read() # POST request
parsed = json.loads(response)

# the object returns has the full usr detaisl, but right now we are only
# interested in the 'token' as this will allow us to interact with the API
# peforming tasks as a logged in user would do on the website. 
userSessionToken = parsed["token"]
print "Successfully logged in, token is " + userSessionToken
