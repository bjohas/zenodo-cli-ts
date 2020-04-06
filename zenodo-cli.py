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

if config.get('env') == 'sandbox':
    ZENODO_API_URL = 'https://sandbox.zenodo.org/api/deposit/depositions'
else:
    ZENODO_API_URL = 'https://zenodo.org/api/deposit/depositions'


def parseId(id):
    slash_split = id.split('/')[-1]
    if slash_split.isnumeric():
        id = slash_split
    else:
        dot_split = id.split('.')[-1]
        if dot_split.isnumeric():
            id = dot_split
    return id


def publishDeposition(id):
    id = parseId(id)
    res = requests.post(
        '{}/{}/actions/publish'.format(ZENODO_API_URL, id), params=params)
    if res.status_code != 202:
        print('Error in publshing deposition {}: {}'.format(
            id, json.loads(res.content)))
    else:
        print('Deposition {} successfully published.'.format(id))


def getData(id):
    # Fetch the original deposit metadata
    id = parseId(id)
    res = requests.get(
        '{}/{}'.format(ZENODO_API_URL, id),
        params=params)
    if res.status_code != 200:
        sys.exit('Error in getting data: {}'.format(json.loads(res.content)))
    return res.json()


def getMetadata(id):
    # Fetch the original deposit metadata
    return getData(id)['metadata']


def parseIds(genericIds):
    return [parseId(id) for id in genericIds]


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
    res = requests.post(ZENODO_API_URL, json={
                        'metadata': metadata}, params=params)
    if res.status_code != 201:
        sys.exit('Error in creating new record: {}'.format(
            json.loads(res.content)))
    response_data = res.json()
    return response_data


def updateRecord(metadata):
    # Creating record metadata
    print('\tUpdating record.')
    res = requests.put(ZENODO_API_URL, json={
        'metadata': metadata}, params=params)
    if res.status_code != 200:
        sys.exit('Error in updating record. {}'.format(
            json.loads(res.content)))
    response_data = res.json()
    return response_data


def fileUpload(bucket_url, journal_filepath):
    # File upload
    print('\tUploading file.')
    # Upload file.
    with open(journal_filepath, 'rb') as fp:
        replaced = re.sub('^.*\/', '', journal_filepath)
        res = requests.put(bucket_url + '/' + replaced, data=fp, params=params)
    if res.status_code != 200:
        sys.exit('Error in creating file upload: {}'.format(
            json.loads(res.content)))
    # notify user
    print('\tUpload successful.')
    # open deposit url so that the user can edit.
    print('\tNew deposit for {0} created; bucket_url {1}'.format(
        journal_filepath, bucket_url))


def duplicate(args):
    metadata = getMetadata(args.id[0])
    del metadata['doi']  # remove the old DOI
    metadata['prereserve_doi'] = True

    # This needs to be fixed to allow multiple titles to create multiple records
    if args.title:
        metadata['title'] = args.title
    if args.date:
        metadata['publication_date'] = args.date
    response_data = createRecord(metadata)

    # Get bucket_url
    bucket_url = response_data['links']['bucket']
    deposit_url = response_data['links']['html']
    print('---')
    print('Title: ' + metadata['title'])
    print('Deposit: ' + deposit_url)
    print('Bucket: ' + bucket_url)

    if args.files:
        for filePath in args.files:
            fileUpload(bucket_url, filePath)

    if args.publish:
        publishDeposition(response_data.id)

    if args.open:
        webbrowser.open_new_tab(deposit_url)


def upload(args):
    bucket_url = None
    if args.bucketurl:
        bucket_url = args.bucketurl
    elif args.id:
        response = getData(args.id)
        bucket_url = response['links']['bucket']
        deposit_url = response['links']['html']
    if bucket_url:
        for filePath in args.files:
            fileUpload(bucket_url, filePath)
        if args.publish and args.id:
            publishDeposition(args.id)
        if args.open and deposit_url:
            webbrowser.open_new_tab(deposit_url)
    else:
        print('Unable to upload: id and bucketurl both not specified.')


def update(args):
    metadata = getMetadata(args.id[0])

    # This needs to be fixed to allow multiple titles to create multiple records
    if args.title:
        metadata['title'] = args.title
    if args.date:
        metadata['publication_date'] = args.date
    response_data = createRecord(metadata)

    # Get bucket_url
    bucket_url = response_data['links']['bucket']
    deposit_url = response_data['links']['html']
    print('---')
    print('Title: ' + metadata['title'])
    print('Deposit: ' + deposit_url)
    print('Bucket: ' + bucket_url)

    if args.files:
        for filePath in args.files:
            fileUpload(bucket_url, filePath)

    if args.publish:
        publishDeposition(response_data.id)

    if args.open:
        webbrowser.open_new_tab(deposit_url)


parser = argparse.ArgumentParser(description='Zenodo command line utility')
subparsers = parser.add_subparsers(help='sub-command help')

parser_get = subparsers.add_parser(
    'get', help='The get command gets the ids listed, and writes these out to id1.json, id2.json etc. The id can be provided as a number, as a deposit URL or record URL')
parser_get.add_argument('id', nargs='*')
parser_get.add_argument('--publish', action='store_true', default=False)
parser_get.add_argument('--open', action='store_true', default=False)
parser_get.set_defaults(func=saveIdsToJson)

parser_duplicate = subparsers.add_parser(
    'duplicate', help='The duplicate command duplicates the id to a new id, optionally providing a title and date and file(s).')
parser_duplicate.add_argument('id', nargs=1)
parser_duplicate.add_argument('--title', action='store')
parser_duplicate.add_argument('--date', action='store')
parser_duplicate.add_argument('--files', nargs='*')
parser_duplicate.add_argument('--publish', action='store_true', default=False)
parser_duplicate.add_argument('--open', action='store_true', default=False)
parser_duplicate.set_defaults(func=duplicate)

parser_upload = subparsers.add_parser('upload')
parser_upload.add_argument('id', nargs='?')
parser_upload.add_argument('--bucketurl', action='store')
parser_upload.add_argument('files', nargs='*')
parser_upload.add_argument('--publish', action='store_true', default=False)
parser_upload.add_argument('--open', action='store_true', default=False)
parser_upload.set_defaults(func=upload)

parser_update = subparsers.add_parser(
    'update', help='The update command updates the id provided, with the title / date and files provided.')
parser_update.add_argument('id', nargs=1)
parser_update.add_argument('--title', action='store')
parser_update.add_argument('--date', action='store')
parser_update.add_argument('--files', nargs='*')
parser_update.add_argument('--publish', action='store_true', default=False)
parser_update.add_argument('--open', action='store_true', default=False)
parser_update.set_defaults(func=update)

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args.func(args)
action = sys.argv[1]

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
