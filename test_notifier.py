#!/usr/bin/env python3

import os
import glob
import sys
import requests
import json
from google.cloud import storage


def upload_html(html_path, gcs_bucket, destination_blob_name, project_id):
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket)

    try:
        if os.path.isdir(html_path):
            for local_file in glob.glob(html_path + '/**'):
                remote_path = '%s%s' %(destination_blob_name, local_file[0 + len(html_path):])
                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_file)

                print(
                    'File {} uploaded to {}.'.format(
                        local_file, destination_blob_name
                    )
                )
            
            if os.path.isfile(html_path + '/index.html'):
                bucket_url = 'https://storage.googleapis.com/%s/%s/index.html' %(gcs_bucket, destination_blob_name)
            elif os.path.isfile(html_path + '/index.htm'):
                bucket_url = 'https://storage.googleapis.com/%s/%s/index.htm' %(gcs_bucket, destination_blob_name)
            else:
                bucket_url = 'https://storage.googleapis.com/%s/%s' %(gcs_bucket, destination_blob_name)

            return  bucket_url
        else:
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(html_path)

            print(
                'File {} uploaded to {}.'.format(
                    html_path, destination_blob_name
                )
            )
            return blob.public_url
    except Exception as e:
        print('Unexpected error:', e)


def post_to_slack(slack_channel, slack_text, build_id, project_id, webhook_url, repo_name, branch_name, commit):
    slack_user_name = 'ReportBot'
    cloudbuild_url = 'https://console.cloud.google.com/cloud-build/builds/%s?project=%s' %(build_id, project_id)
    slack_data = {
        'channel': slack_channel,
        'text': '%s test suite has completed' %(repo_name),
        'username': slack_user_name,
        'blocks': [
            {  
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': ':tada: %s test suite has completed.' %(repo_name)
                }
            },
			{
				'type': 'section',
				'fields': [
					{
						'type': 'mrkdwn',
						'text': '*Repo Name:*\n %s' %(repo_name)
					},
					{
						'type': 'mrkdwn',
						'text': '*Branch Name:*\n %s \n' %(branch_name)
					}
				]
			},
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*Commit:*\n %s' %(commit)
                }
            },
            {
                'type': 'actions',
                'block_id': 'view_test_result',
                'elements': [
                    {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': 'View Test Result'
                        },
                        'style': 'primary',
                        'url': slack_text
                    },
                    {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': 'View Cloudbuild Run'
                        },
                        'url': cloudbuild_url
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
    # Get environment variables
    html_path = os.environ.get('HTML_PATH')
    gcs_bucket = os.environ.get('GCS_BUCKET')
    destination_blob_name = os.environ.get('BLOB_NAME')
    slack_channel = os.environ.get('SLACK_CHANNEL')
    build_id = os.environ.get('BUILD_ID')
    project_id = os.environ.get('PROJECT_ID')
    webhook_url = os.environ.get('WEBHOOK_URL')
    repo_name = os.environ.get('REPO_NAME')
    branch_name = os.environ.get('BRANCH_NAME')
    commit = os.environ.get('COMMIT_SHA')

    # upload test file/folders to GCS
    test_url = upload_html(html_path, gcs_bucket, destination_blob_name, project_id)

    # post notification to slack
    post_to_slack(slack_channel, test_url, build_id, project_id, webhook_url, repo_name, branch_name, commit)

if __name__ == '__main__':
    main()
