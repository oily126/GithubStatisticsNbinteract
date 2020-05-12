#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 
import numpy as np
import json, datetime
from json_helpers import extract_datetime

# tweak here the names of the github org and repo to analyse
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

FILENAME_WEBRTC_COUNTS = 'WebRTC_counts.csv'
FILENAME_PRODUCER_COUNTS = 'Producer_counts.csv'



#BUG_LABEL = ['bug']

def load_file(FILENAME):
    with open(FILENAME, encoding='utf-8', errors='ignore') as json_data:
        data = json.load(json_data, strict=False)
    return data

def get_first_date(REPOS, data):
    first_dates = []
    for REPO in REPOS:
        if REPO not in data.keys() and len(data[REPO]) == 0:
            raise SystemExit()

        # convert all date strings to datetime objects
        for i in data[REPO].keys():
            data[REPO][i]['created_at'] = extract_datetime(data[REPO][i]['created_at'])
            if data[REPO][i]['closed_at'] is not None:
                data[REPO][i]['closed_at'] = extract_datetime(data[REPO][i]['closed_at'])

        # retrieve highest issue number
        last_number = min([int(i) for i in data[REPO].keys()])
        first_dates.append(extract_datetime(data[REPO][str(last_number)]['created_at']))    
        
    first_date = datetime.date.today()
    #print(first)
    for date in first_dates:
        day = date.date()
        if (day < first_date):
            first_date = day

    return first_date

def get_results(REPOS, FILENAME_ISSUES, FILENAME_COUNTS):
    
    data = load_file(FILENAME_ISSUES)
    
    first_date = get_first_date(REPOS, data)
    print(first_date)
    
    day = datetime.datetime(first_date.year, first_date.month, first_date.day, tzinfo=datetime.timezone.utc)
    day += one_day

    result = {}

    f = open(FILENAME_COUNTS, 'w')
    f.write('date, total_issues, open_issues, closed_issue, open_prs, closed_prs, ranking')
    #f.write('date\topen_issues\tclosed_issues\topen_prs\tclosed_prs\tranking\t%s\n'%'\t'.join(APP_LABEL))
    
    while day < now:
        key = day.strftime('%Y-%m-%d')
        #print(key)

        open_pr_count = 0
        closed_pr_count = 0
        open_issue_count = 0
        closed_issue_count = 0
        total_issue_count = 0
        rating_number = 0
        rating_apps = {}

        for REPO in REPOS:   
            for i in data[REPO]:
                element = data[REPO][i]

                if element['created_at'] > day:
                    continue

                #print(element)
                is_open = True
                total_issue_count += 1
                if isinstance(element['closed_at'], datetime.datetime) and element['closed_at'] < day:
                    is_open = False
                    closed_issue_count += 1
                else: 
                    open_issue_count += 1


        output = '%s,%i,%i,%i,%i,%i'%(key, total_issue_count, open_issue_count, closed_issue_count, open_pr_count, closed_pr_count)
        #print(output)
        f.write(output + '\n')

        day += one_day

    f.close()

def get_df(FILENAME):
    df=pd.read_csv(FILENAME, parse_dates = ['date'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.rename(columns = {' total_issues':'total_issues', ' open_issues':'open_issues', 
                                  ' closed_issue':'closed_issues'}, inplace = True) 
    df = df.filter(['date','total_issues','open_issues','closed_issues'])
    
    idx = pd.date_range(df.index[0], df.index[-1])
    df = df.reindex(idx, fill_value=0)
    df['Month_End'] = df.index.is_month_end
    sample_df = df[df['Month_End'] == 1].copy()
    sample_df = sample_df.drop(['Month_End'], axis=1)
    
    sLength = len(sample_df['total_issues'])
    #print(sLength)
    issues_opened =  pd.Series(np.zeros(sLength))
    issues_closed =  pd.Series(np.zeros(sLength))
    sample_df = sample_df.assign(issues_opened=issues_opened.values)
    sample_df = sample_df.assign(issues_closed=issues_closed.values)
    sample_df.head()
    
    sample_df['issues_opened'] = sample_df.total_issues.shift().fillna(0) 
    sample_df['issues_closed'] = sample_df.closed_issues.shift().fillna(0) 

    sample_df['issues_opened'] = sample_df['total_issues'] - sample_df['issues_opened']
    sample_df['issues_closed'] = sample_df['closed_issues'] - sample_df['issues_closed']

    sample_df.head()
    
    return sample_df

one_day = datetime.timedelta(days=1)
now = datetime.datetime.now(datetime.timezone.utc)

get_results(PRODUCER_REPOS, FILENAME_PRODUCER_ISSUES, FILENAME_PRODUCER_COUNTS)
get_results(WEBRTC_REPOS, FILENAME_WEBRTC_ISSUES, FILENAME_WEBRTC_COUNTS)

df_producer = get_df(FILENAME_PRODUCER_COUNTS)
df2 = df_producer[['open_issues', 'issues_opened', 'issues_closed']]
ax = df2.plot(title='Producer SDK Github Issues');
ax.figure.savefig('ProducerSDKGithubIssues.png')

df_webrtc = get_df(FILENAME_WEBRTC_COUNTS)
df2 = df_webrtc[['open_issues', 'issues_opened', 'issues_closed']]
ax = df2.plot(title = 'WebRTC SDK Github Issues');
ax.figure.savefig('WebRTCSDKGithubIssues.png')