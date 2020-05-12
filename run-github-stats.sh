#!/bin/bash
python import_issues_multirepo.py --token=$1
python process_issues_multirepo.py
aws s3 cp ProducerSDKGithubIssues.png s3://$2/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp WebRTCSDKGithubIssues.png s3://$2/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers

