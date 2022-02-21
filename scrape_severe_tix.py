
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time

# SET GLOBALS - make env_var before committing
API_TOKEN = os.environ['JIRA_API_TOKEN']
JIRA_DOMAIN = os.environ['JIRA_DOMAIN']
JIRA_EMAIL= os.environ['JIRA_EMAIL']
CACHE_PATH = "./data/"

def scrape_jira_tix():
    # setup API
    url = "https://" + JIRA_DOMAIN + ".atlassian.net/rest/api/3/search"
    auth = HTTPBasicAuth(JIRA_EMAIL, API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # form query for high+ severity, specify fields to return
    query = 'project = "TTT" AND priority IN ("High","Highest") ORDER BY created DESC'
    fields = ['id', 'priority', 'created', 'summary']

    # page through results
    index = 0
    total = 1
    maxResults = None
    while total > index:  # make sure the previous query contained the last ticket
        print("DEBUG 1: ", index, total, maxResults)
        params = {
            'jql': query,
            'fields': fields,
            'startAt': index
        }
        response = requests.request(
            "GET",
            url,
            params=params,
            headers=headers,
            auth=auth
        )
        # no error handling for now
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        # update values
        total = response.json()['total']
        maxResults = response.json()['maxResults']
        index = index + maxResults - 1
        print("DEBUG 2: ", index, total, maxResults)
        # cache data for db upload service
        try:
            cache_to_file(response.json())
        except Exception as e:
            raise(e)

# save file locally
def cache_to_file(data):
    output_file = CACHE_PATH + str(int(time.time())) + "-scrape.json"
    with open(output_file, 'w') as f:
        json.dump(data, f)
    print('data saved: ', output_file)
    time.sleep(2)


if __name__ == "__main__":
    scrape_jira_tix()
