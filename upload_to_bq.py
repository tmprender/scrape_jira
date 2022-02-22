from google.cloud import bigquery
from google.cloud import storage
import json
from datetime import datetime

BUCKET_NAME = "<bucket_name>"
TABLE_ID = "<project_id>.<data_set>.<table_name>" 


# triggered on file upload to Cloud Storage,
# pulls filename and uploads contents to BigQuery

def gcs_to_bq(event, context):
    print("DEBUG: ", event)
    # get filename from event
    filename = event['name']
    # get file from storage
    local_file = get_contents(filename)
    # parse file for jira issue info
    rows_to_insert = parse_file_for_jira_info(local_file)
    # update table, bulk upload rows defind in json
    result = add_rows_to_bq(rows_to_insert)

def get_contents(filename):
    # get file from bucket, save locally
    gcs = storage.Client()
    bucket = gcs.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)  # prepare the object for file download
    local_file = "/tmp/" + filename  # local filename - save to /tmp/ on runtime container (cloud function)
    blob.download_to_filename(local_file)  # save object as local file

    return local_file

# returns rows to insert into bq table
def parse_file_for_jira_info(local_file):
    with open(local_file) as f:
        issues = json.loads(f.read())['issues']
    
    # map function for formatting JIRA issue info into table schema
    def format_issue_for_query(issue):
        # parse timestamp for SQL
        timestamp = issue['fields']['created']
        timestamp = timestamp[0:timestamp.find(".")]  # strip milliseconds
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        timestamp = datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S")
        # format rest of query
        result = {
            u'id': issue['id'], u'priority': issue['fields']['priority']['name'],
            u'created': timestamp, u'summary': issue['fields']['summary']
        }
        return result

    rows_to_insert = list(map(format_issue_for_query, issues))
    return rows_to_insert

def add_rows_to_bq(rows_to_insert):
    bq = bigquery.Client()

    errors = bq.insert_rows_json(TABLE_ID, rows_to_insert)  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
   