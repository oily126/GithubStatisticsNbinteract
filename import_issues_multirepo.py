#!/usr/bin/env python
# -*- coding: utf-8 -*-

import github3, json, os.path
import argparse

from json_helpers import DateTimeEncoder

ORG = 'awslabs'

WEBRTC_REPOS = ['amazon-kinesis-video-streams-webrtc-sdk-c', 
                'amazon-kinesis-video-streams-webrtc-sdk-ios', 
                'amazon-kinesis-video-streams-webrtc-sdk-android']
PRODUCER_REPOS = ['amazon-kinesis-video-streams-producer-sdk-cpp', 
                  'amazon-kinesis-video-streams-producer-c', 
                  'amazon-kinesis-video-streams-producer-sdk-java', 
                  'amazon-kinesis-video-streams-pic']
FILENAME_WEBRTC_ISSUES = 'WebRTC_issues.json'
FILENAME_PRODUCER_ISSUES = 'Producer_issues.json'

def get_issues(REPOS, FILENAME):
    data = {}
    #if os.path.isfile(FILENAME):
    #    f = open(FILENAME_WEBRTC_ISSUES)
    #    data = json.load(f)
    #    f.close()
        
    for REPO in REPOS:
        print(REPO)
        data[REPO] = {}
        for i in gh.issues_on(ORG, REPO, state='all'):
            data[REPO][i.number] = {
                'created_at': i.created_at,
                'closed_at': i.closed_at,
                'is_pull_request': (i.pull_request is not None)
            }
            
    f = open(FILENAME, 'w')
    json.dump(data, f, cls=DateTimeEncoder)
    f.close()

parser = argparse.ArgumentParser(description='Script to handle GitHub Issue statistics!')
parser.add_argument("--token", default="", help="This is the GitHub Dev Token variable")

args = parser.parse_args()
GITHUB_TOKEN = args.token
gh = github3.login(token=GITHUB_TOKEN)
print(gh)
get_issues(WEBRTC_REPOS, FILENAME_WEBRTC_ISSUES)  
get_issues(PRODUCER_REPOS, FILENAME_PRODUCER_ISSUES)