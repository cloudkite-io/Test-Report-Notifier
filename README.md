# e2e-test-report

This repo contains a python script which has been baked into a docker image that can be used in a cloudbuild build step and will do the following:
- take env vars for: HTML_PATH, GCS_BUCKET, PROJECT_ID, SLACK_CHANNEL and WEBHOOK_URL.
- copy the files in the html/artifact path to the GCS bucket
- post the link to the GCS object to slack so that a user in slack and click on the link to view the cloud build artifacts as well as a link to the cloubuild run itself.
