#!/usr/bin/env python3

import os
import sys
import requests
import json
from google.cloud import storage


def upload_html():
    """Uploads a file to the bucket."""
    html_path = os.environ.get('HTML_PATH')
    gcs_bucket = os.environ.get('GCS_BUCKET')
    destination_blob_name = os.environ.get('BLOB_NAME')
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(html_path)

        print(
            "File {} uploaded to {}.".format(
                html_path, destination_blob_name
            )
        )
        print(blob.public_url)
        return blob.public_url
    except Exception as e:
        print("Unexpected error:", e)


def post_to_slack(slack_text):
    slack_channel = os.environ.get('SLACK_CHANNEL')
    slack_user_name = 'E2E Test Report'
    build_id = os.environ.get('BUILD_ID')
    project_id = os.environ.get('PROJECT_ID')
    webhook_url = os.environ.get('WEBHOOK_URL')
    cloudbuild_url = 'https://console.cloud.google.com/cloud-build/builds/%s?project=%s' %(build_id, project_id)
    slack_data = {
        'channel': slack_channel,
        'text': "E2E Test Completed",
        'username': slack_user_name,
        'blocks': [
            {  
                "type": "section",
                "text": {  
                    "type": "mrkdwn",
                    "text": ":tada: E2E test completed successfully."
                }
            },
            {
                "type": "actions",
                "block_id": "view_test_result",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Test Result"
                        },
                        "style": "primary",
                        "url": slack_text
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Cloudbuild Run"
                        },
                        "url": cloudbuild_url
                    }
                ]
            }
        ]
    }


    response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
    )


def main():
    test_url = upload_html()
    post_to_slack(test_url)

if __name__ == "__main__":
    main()


