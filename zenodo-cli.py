#!/usr/bin/python
# Read this first https://developers.zenodo.org/#quickstart-upload
# https://github.com/bjohas/Zenodo-tools

import requests
import sys
import re
import webbrowser
import json
import argparse

config = json.load(open('./.config.json'))

params = {'access_token': config.get('accessToken')}

ZENODO_API_URL = 'https://zenodo.org/api/deposit/depositions/'


def publishDeposition(id):
    res = requests.post(
        '{}{}/actions/publish'.format(ZENODO_API_URL, id), params=params)
    if res.status_code != 200:
        print('Error in publshing deposition {}: {}'.format(
            id, json.loads(res.content)))
    else:
        print('Deposition {} successfully published.'.format(id))


def getData(id):
    # Fetch the original deposit metadata
    res = requests.get(
        'https://zenodo.org/api/deposit/depositions/{}'.format(id),
        params=params)
    if res.status_code != 200:
        sys.exit('Error in getting ORIGINAL_DEPOSIT')
    return res.json()


def getMetadata(ORIGINAL_DEPOSIT_ID):
    # Fetch the original deposit metadata
    return getData(ORIGINAL_DEPOSIT_ID)['metadata']


def parseIds(genericIds):
    ids = []
    for id in genericIds:
        slash_split = id.split('/')[-1]
        if slash_split.isnumeric():
            ids.append(slash_split)
        else:
            dot_split = id.split('.')[-1]
            if dot_split.isnumeric():
                ids.append(dot_split)
    return ids


def saveIdsToJson(args):
    ids = parseIds(args.id)
    for id in ids:
        with open('{}.json'.format(id), 'w') as f:
            data = getData(id)
            json.dump(data['metadata'], f)
        if args.publish:
            publishDeposition(id)
        if args.open:
            webbrowser.open_new_tab(data['links']['html'])


def createRecord(metadata):
    # Creating record metadata
    print('\tCreating record.')
    res = requests.post(
        'https://zenodo.org/api/deposit/depositions',
        json={'metadata': metadata}, params=params)
    if res.status_code != 201:
        sys.exit('Error in creating new record. '+format(res.status_code))
    response_data = res.json()
    # Print the URL of the deposit
    deposit_url = response_data['links']['html']
    print('\tNew deposit created at {0}'.format(deposit_url))
    # open deposit url so that the user can edit.
    webbrowser.open_new_tab(deposit_url)
    return response_data


def fileUpload(bucket_url, journal_filepath):
    # File upload
    print('\tUploading file.')
    # Upload file.
    with open(journal_filepath, 'rb') as fp:
        res = requests.put(bucket_url + '/' + replaced, data=fp, params=params)
    if res.status_code != 200:
        sys.exit('Error in creating file upload.')
    # notify user
    print('\tUpload successful.')
    # open deposit url so that the user can edit.
    print('\tNew deposit for {0} created; bucket_url {1}'.format(
        journal_filepath, bucket_url))
    webbrowser.open_new_tab(deposit_url)


parser = argparse.ArgumentParser(description='Zenodo command line utility')
subparsers = parser.add_subparsers(help='sub-command help')

parser_get = subparsers.add_parser(
    'get', help='The get command gets the ids listed, and writes these out to id1.json, id2.json etc. The id can be provided as a number, as a deposit URL or record URL')
parser_get.add_argument('id', nargs='*')
parser_get.add_argument('--publish', action='store_true', default=False)
parser_get.add_argument('--open', action='store_true', default=False)
parser_get.set_defaults(func=saveIdsToJson)


if len(sys.argv) < 2:
    print("Usage: zenodo-cli <action> ... ")
    print("       zenodo-cli get deposit_id")
    print("       zenodo-cli create file1.json [file2.json [file3.json ...]]")
    print("       zenodo-cli duplicate original_deposit_id [title]")
    print("       zenodo-cli upload bucketurl file.pdf")
    print(
        "       zenodo-cli copy original_deposit_id file1.pdf [file2.pdf [file3.pdf ...]]")
    print("       zenodo-cli adapt original_deposit_id title date file1.pdf")
    sys.exit('ERROR: Too few arguments.')

args = parser.parse_args()
args.func(args)
action = sys.argv[1]

'''
if action == "get":
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    metadata = getMetadata(ORIGINAL_DEPOSIT_ID)
    print(metadata)
'''

if action == "create":
    JSON_FILES = sys.argv[2:len(sys.argv)]

    '''
    metadata = getMetadata(ORIGINAL_DEPOSIT_ID)
    del metadata['doi']
    # Do not allocate a DOI
    del metadata['prereserve_doi']
    '''

    # Create new deposits based on the original metadata
    for json_filepath in JSON_FILES:
        print('Processing: '+json_filepath)
        replaced = re.sub('^.*\/', '', json_filepath)
        print('\tfilename: '+replaced)
        file = open(json_filepath, mode='r')
        metadata = file.read()
        file.close()
        response_data = createRecord(metadata)


if action == "duplicate":
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    TITLES = sys.argv[3:len(sys.argv)]
    metadata = getMetadata(ORIGINAL_DEPOSIT_ID)
    del metadata['doi']  # remove the old DOI
    metadata['prereserve_doi'] = True

    # This needs to be fixed to allow multiple titles to create multiple records
    if TITLES:
        metadata['title'] = TITLES[0]

    response_data = createRecord(metadata)

    # Get bucket_url
    bucket_url = response_data['links']['bucket']
    deposit_url = response_data['links']['html']
    print('---')
    print('Title: ' + metadata['title'])
    print('Deposit: '+deposit_url)
    print('Bucket: '+bucket_url)

if action == "upload":
    bucket_url = sys.argv[2]
    journal_filepath = sys.argv[3]
    replaced = re.sub('^.*\/', '', journal_filepath)
    fileUpload(bucket_url, journal_filepath)

if action == "copy":
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    # Modify the list accordingly...
    JOURNAL_FILES = sys.argv[3:len(sys.argv)]

    metadata = getMetadata(ORIGINAL_DEPOSIT_ID)
    del metadata['doi']  # remove the old DOI
    del metadata['prereserve_doi']

    # Create new deposits based on the original metadata
    for journal_filepath in JOURNAL_FILES:
        # Notify user of file to be uploaded.
        print('Processing: '+journal_filepath)
        replaced = re.sub('^.*\/', '', journal_filepath)
        print('\tfilename: '+replaced)

        response_data = createRecord(metadata)

        # Get bucket_url
        bucket_url = response_data['links']['bucket']

        fileUpload(bucket_url, journal_filepath)

#     print("       zenodo-cli adapt original_deposit_id title date file1.pdf")

if action == "adapt":
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    title = sys.argv[3]
    DATE = sys.argv[4]
    journal_filepath = sys.argv[5]

    metadata = getMetadata(ORIGINAL_DEPOSIT_ID)

    del metadata['doi']  # remove the old DOI
    del metadata['prereserve_doi']

    metadata['title'] = title
    metadata['publication_date'] = DATE
    metadata['description'] = '<p>For more information please visit https://opendeved.net.</p>'

    # Notify user of file to be uploaded.
    print('Processing: '+journal_filepath)
    replaced = re.sub('^.*\/', '', journal_filepath)
    print('\tfilename: '+replaced)

    response_data = createRecord(metadata)

    # Get bucket_url
    bucket_url = response_data['links']['bucket']

    fileUpload(bucket_url, journal_filepath)
