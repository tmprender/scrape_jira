import os
import requests
from requests.auth import HTTPBasicAuth
import json
import random
import time

# SET GLOBALS
API_TOKEN = os.environ['JIRA_API_TOKEN']
JIRA_DOMAIN = os.environ['JIRA_DOMAIN']
JIRA_EMAIL= os.environ['JIRA_EMAIL']

# setup API
url = "https://" + JIRA_DOMAIN + ".atlassian.net/rest/api/3/issue"
auth = HTTPBasicAuth(JIRA_EMAIL, API_TOKEN)
headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}

# create 100 tickets with random severity for 1 hour
tickets_created = 0 
while tickets_created < 101:
    severity = random.randrange(1,5)  # 1="Highest", 5="Lowest"

    # define the JIRA issue and build payload
    body = {
        "update": {},
        "fields": {
            "summary": "random_issue_" + str(tickets_created * severity),  # multiply by severity to randomize(-ish)
            "project": {
                "id": "10000"
            },
            "issuetype": {
                "id": "10004"  # consider randomizing
            },
            "priority": {
                "id": str(severity)
            },
        },
    }
    payload = json.dumps(body)

    # make API call
    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    print("DEBUG: ", type(response), response, response.text)

    # check response
    if response.json().get("id"):
        tickets_created += 1
    else:
        # error - move to try/except
        print(response)

    # pace API calls over 60 minutes
    time.sleep(10 * severity)



#print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
#print(type(response), response, response.text)