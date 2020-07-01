#!/usr/bin/python3
# Read this first https://developers.zenodo.org/#quickstart-upload
# https://github.com/bjohas/Zenodo-tools

import requests
import sys
import re
import webbrowser
import json
import argparse
import pprint
from pathlib import Path
import os

params = {}
ZENODO_API_URL = ''
FALLBACK_CONFIG_FILE = os.environ['HOME'] + '/.config/zenodo-cli/config.json'


def loadConfig(configFile):
    global params
    global ZENODO_API_URL
    if Path(configFile).is_file():
        configFile = configFile
    elif Path(FALLBACK_CONFIG_FILE).is_file():
        configFile = FALLBACK_CONFIG_FILE
    else:
        print('Config file not present at {} or {}'.format(
            'config.json', FALLBACK_CONFIG_FILE))
        sys.exit(1)

    config = json.load(open(configFile))
    params = {'access_token': config.get('accessToken')}

    if config.get('env') == 'sandbox':
        ZENODO_API_URL = 'https://sandbox.zenodo.org/api/deposit/depositions'
    else:
        ZENODO_API_URL = 'https://zenodo.org/api/deposit/depositions'


def parseId(id):
    if str(id).isnumeric():
        return id
    slash_split = str(id).split('/')[-1]
    if slash_split.isnumeric():
        id = slash_split
    else:
        dot_split = str(id).split('.')[-1]
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
        print('\tDeposition {} successfully published.'.format(id))


def getData(id):
    # Fetch the original deposit metadata
    id = parseId(id)
    res = requests.get(
        '{}/{}'.format(ZENODO_API_URL, id),
        params=params)
    if res.status_code != 200:
        print('Error in getting data: {}'.format(json.loads(res.content)))
        sys.exit(1)

    return res.json()


def showDepositionJSON(info):
    print('Title: {}'.format(info['title']))
    print('Date: {}'.format(info['metadata']['publication_date']))
    print('RecordId: {}'.format(info['id']))
    if ('conceptrecid' in info.keys()):
        print('ConceptId: {}'.format(info['conceptrecid']))
    else:
        print('ConceptId: N/A')
    print('DOI: {}'.format(info['metadata']['prereserve_doi']['doi']))
    print('Published: {}'.format('yes' if info['submitted'] else 'no'))
    print('State: {}'.format(info['state']))
    print(
        'URL: https://zenodo.org/{}/{}'.format('record' if info['submitted'] else 'deposit', info['id']))
    if ('bucket' in info['links'].keys()):
        print('BucketURL: {}'.format(info['links']['bucket']))
    else:
        print('BucketURL: N/A')
    print('\n')


def showDeposition(id):
    id = parseId(id)
    info = getData(id)
    showDepositionJSON(info)


def dumpJSON(info):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(info)
    print('\n')


def dumpDeposition(id):
    id = parseId(id)
    info = getData(id)
    dumpJSON(info)


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
        finalActions(args, id, data['links']['html'])


def createRecord(metadata):
    # Creating record from metadata
    print('\tCreating record.')
    res = requests.post(ZENODO_API_URL, json={
                        'metadata': metadata}, params=params)
    if res.status_code != 201:
        print('Error in creating new record: {}'.format(
            json.loads(res.content)))
        sys.exit(1)
    response_data = res.json()
    return response_data


def editDeposit(dep_id):
    # Make deposition editable.
    dep_id = parseId(dep_id)
    res = requests.post(
        '{}/{}/actions/edit'.format(ZENODO_API_URL, dep_id), params=params)

    if res.status_code != 201:
        print('Error in making record editable. {}'.format(
            json.loads(res.content)))
        sys.exit(1)

    response_data = res.json()
    return response_data


def updateRecord(dep_id, metadata):
    # Creating record metadata
    print('\tUpdating record.')
    dep_id = parseId(dep_id)
    res = requests.put(ZENODO_API_URL + '/' + dep_id, json={
        'metadata': metadata}, params=params)
    if res.status_code != 200:
        print('Error in updating record. {}'.format(
            json.loads(res.content)))
        sys.exit(1)
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
        print('Error in creating file upload: {}'.format(
            json.loads(res.content)))
        sys.exit(1)
    # notify user
    print('\tUpload successful.')


def duplicate(args):
    metadata = getMetadata(args.id[0])
    del metadata['doi']  # remove the old DOI
    metadata['prereserve_doi'] = True

    metadata = updateMetadata(args, metadata)
    response_data = createRecord(metadata)

    # Get bucket_url
    bucket_url = response_data['links']['bucket']
    deposit_url = response_data['links']['html']

    if args.files:
        for filePath in args.files:
            fileUpload(bucket_url, filePath)

    finalActions(args, response_data['id'], deposit_url)


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
        finalActions(args, args.id, deposit_url)
    else:
        print('Unable to upload: id and bucketurl both not specified.')


def updateMetadata(args, metadata):
    if 'title' in args.__dict__ and args.title:
        metadata['title'] = args.title
    if 'date' in args.__dict__ and args.date:
        metadata['publication_date'] = args.date
    if 'description' in args.__dict__ and args.description:
        metadata['description'] = args.description
    if 'add_communites' in args.__dict__ and args.add_communites:
        metadata['communities'] = [{'identifier': community}
                                   for community in args.add_communities]
    if 'remove_communities' in args.__dict__ and args.remove_communities:
        metadata['communities'] = list(filter(
            lambda comm: comm['identifier'] not in args.remove_communities, metadata['communities']))
    if 'communities' in args.__dict__ and args.communities:
        with open(args.communities) as comm:
            metadata['communities'] = [{'identifier': community}
                                       for community in comm.read().splitlines()]
    if 'authordata' in args.__dict__ and args.authordata:
        with open(args.authordata) as author_data_fp:
            metadata['creators'] = []
            for author_data in author_data_fp.read().splitlines():
                if author_data.strip():
                    creator = author_data.split('\t')
                    metadata['creators'].append({
                        'name': creator[0],
                        'affiliation': creator[1],
                        'orcid': creator[2]
                    })
    if 'authors' in args.__dict__ and args.authors:
        metadata['creators'] = [{'name': author}
                                for author in args.authors.split(';')]

    if 'zotero_link' in args.__dict__ and args.zotero_link:
        metadata['related_identifiers'] = [
            {
                'identifier': args.zotero_link,
                'relation': 'isAlternateIdentifier',
                'resource_type': 'other',
                'scheme': 'url'
            }
        ]
    if 'json' in args.__dict__ and args.json:
        with open(args.json) as meta_file:
            for (key, value) in json.load(meta_file).items():
                metadata[key] = value

    return metadata


def update(args):
    id = parseId(args.id[0])
    data = getData(id)

    metadata = data['metadata']

    if data['state'] == 'done':
        print('\tMaking record editable.')
        response = editDeposit(id)

    metadata = updateMetadata(args, metadata)

    response_data = updateRecord(id, metadata)

    # Get bucket_url
    bucket_url = response_data['links']['bucket']
    deposit_url = response_data['links']['html']

    if args.files:
        for filePath in args.files:
            fileUpload(bucket_url, filePath)

    finalActions(args, id, deposit_url)


def finalActions(args, id, deposit_url):
    if 'publish' in args.__dict__ and args.publish:
        publishDeposition(id)

    if 'show' in args.__dict__ and args.show:
        showDeposition(id)

    if 'dump' in args.__dict__ and args.dump:
        dumpDeposition(id)

    if 'open' in args.__dict__ and args.open:
        webbrowser.open_new_tab(deposit_url)


def create(args):
    # Create new deposits based on the original metadata
    for json_filepath in args.files:
        print('Processing: ' + json_filepath)
        with open(json_filepath, mode='r') as f:
            metadata = json.loads(f.read())
        metadata = updateMetadata(args, metadata)
        response_data = createRecord(metadata)

        finalActions(args, response_data['id'], response_data['links']['html'])


def copy(args):
    metadata = getMetadata(args.id)
    del metadata['doi']  # remove the old DOI
    del metadata['prereserve_doi']

    # Create new deposits based on the original metadata
    for journal_filepath in args.files:
        # Notify user of file to be uploaded.
        print('Processing: '+journal_filepath)
        response_data = createRecord(metadata)

        # Get bucket_url
        bucket_url = response_data['links']['bucket']
        fileUpload(bucket_url, journal_filepath)
        finalActions(args, response_data['id'], response_data['links']['html'])


def listDepositions(args):
    listParams = params
    listParams['page'] = args.page
    listParams['size'] = args.size if args.size else 1000
    res = requests.get(ZENODO_API_URL, params=listParams)
    if res.status_code != 200:
        print('Failed in listDepositions: {}'.format(
            json.loads(res.content)))
        sys.exit(1)

    if 'dump' in args.__dict__ and args.dump:
        dumpJSON(res.json())

    for dep in res.json():
        print('{} {}'.format(dep['record_id'], dep['conceptrecid']))

        if 'publish' in args.__dict__ and args.publish:
            publishDeposition(dep['id'])

        if 'show' in args.__dict__ and args.show:
            showDepositionJSON(dep)

        if 'open' in args.__dict__ and args.open:
            webbrowser.open_new_tab(dep['links']['html'])


def newVersion(args):
    id = parseId(args.id[0])
    response = requests.post(
        '{}/{}/actions/newversion'.format(ZENODO_API_URL, id), params=params)

    if response.status_code != 201:
        print('New version request failed: {}'. format(
            json.loads(response.content)))
        sys.exit(1)

    response_data = response.json()

    metadata = getMetadata(id)
    newmetadata = updateMetadata(args, metadata)
    if newmetadata != metadata:
        response_data = updateRecord(id, newmetadata)

    bucket_url = response_data['links']['bucket']
    deposit_url = response_data['links']['latest_html']

    if args.files:
        for filePath in args.files:
            fileUpload(bucket_url, filePath)

    finalActions(args, response_data['id'], deposit_url)


parser = argparse.ArgumentParser(description='Zenodo command line utility')
parser.add_argument('--config', action='store', default='config.json',
                    help='Config file with API key. By default config.json then ~/.config/zenodo-cli/config.json are used if no config is provided.')
subparsers = parser.add_subparsers(help='sub-command help')

parser_list = subparsers.add_parser(
    "list", help='List deposits for this account. Note that the Zenodo API does not seem to send continuation tokens. The first 1000 results are retrieved. Please use --page to retrieve more. The result is the record id, followed by the concept id.')
parser_list.add_argument('--page', action='store',
                         help='Page number of the list.')
parser_list.add_argument('--size', action='store',
                         help='Number of records in one page.')
parser_list.add_argument('--publish', action='store_true',
                         help='Publish the depositions after executing the command.', default=False)
parser_list.add_argument('--open', action='store_true',
                         help='Open the depositions in the browser after executing the command.', default=False)
parser_list.add_argument('--show', action='store_true',
                         help='Show key information for the depositions after executing the command.', default=False)
parser_list.add_argument('--dump', action='store_true',
                         help='Show json for list and for depositions after executing the command.', default=False)
parser_list.set_defaults(func=listDepositions)

parser_get = subparsers.add_parser(
    'get', help='The get command gets the ids listed, and writes these out to id1.json, id2.json etc. The id can be provided as a number, as a deposit URL or record URL')
parser_get.add_argument('id', nargs='*')
parser_get.add_argument('--publish', action='store_true',
                        help='Publish the deposition after executing the command.', default=False)
parser_get.add_argument('--open', action='store_true',
                        help='Open the deposition in the browser after executing the command.', default=False)
parser_get.add_argument('--show', action='store_true',
                        help='Show key information for the deposition after executing the command.', default=False)
parser_get.add_argument('--dump', action='store_true',
                        help='Show json for deposition after executing the command.', default=False)
parser_get.set_defaults(func=saveIdsToJson)

parser_create = subparsers.add_parser(
    'create', help='The create command creates new records based on the json files provided, optionally providing a title / date / description / files.')
parser_create.add_argument('files', nargs='*')
parser_create.add_argument('--title', action='store')
parser_create.add_argument('--date', action='store')
parser_create.add_argument('--description', action='store')
parser_create.add_argument('--add-communities', nargs='*')
parser_create.add_argument('--remove-communities', nargs='*')
parser_create.add_argument('--communities', action='store')
parser_create.add_argument('--authordata', action='store')
parser_create.add_argument('--authors', action='store')
parser_create.add_argument('--zotero-link', action='store',
                           help='Zotero link of the zotero record to be linked.')
parser_create.add_argument('--json', action='store',
                           help='Path of the JSON file with the metadata of the zenodo record to be created.')
parser_create.add_argument('--publish', action='store_true',
                           help='Publish the deposition after executing the command.', default=False)
parser_create.add_argument('--open', action='store_true',
                           help='Open the deposition in the browser after executing the command.', default=False)
parser_create.add_argument('--show', action='store_true',
                           help='Show the info of the deposition after executing the command.', default=False)
parser_create.add_argument('--dump', action='store_true',
                           help='Show json for deposition after executing the command.', default=False)
parser_create.set_defaults(func=create)

parser_duplicate = subparsers.add_parser(
    'duplicate', help='The duplicate command duplicates the id to a new id, optionally providing a title / date / description / files.')
parser_duplicate.add_argument('id', nargs=1)
parser_duplicate.add_argument('--title', action='store')
parser_duplicate.add_argument('--date', action='store')
parser_duplicate.add_argument('--files', nargs='*')
parser_duplicate.add_argument('--description', action='store')
parser_duplicate.add_argument('--publish', action='store_true',
                              help='Publish the deposition after executing the command.', default=False)
parser_duplicate.add_argument('--open', action='store_true',
                              help='Open the deposition in the browser after executing the command.', default=False)
parser_duplicate.add_argument('--show', action='store_true',
                              help='Show the info of the deposition after executing the command.', default=False)
parser_duplicate.add_argument('--dump', action='store_true',
                              help='Show json for deposition after executing the command.', default=False)
parser_duplicate.set_defaults(func=duplicate)

parser_update = subparsers.add_parser(
    'update', help='The update command updates the id provided, with the title / date / description / files provided.')
parser_update.add_argument('id', nargs=1)
parser_update.add_argument('--title', action='store')
parser_update.add_argument('--date', action='store')
parser_update.add_argument('--description', action='store')
parser_update.add_argument('--files', nargs='*')
parser_update.add_argument('--add-communities', nargs='*')
parser_update.add_argument('--remove-communities', nargs='*')
parser_update.add_argument('--zotero-link', action='store',
                           help='Zotero link of the zotero record to be linked.')
parser_update.add_argument('--json', action='store',
                           help='Path of the JSON file with the metadata of the zenodo record to be updated.')
parser_update.add_argument('--publish', action='store_true',
                           help='Publish the deposition after executing the command.', default=False)
parser_update.add_argument('--open', action='store_true',
                           help='Open the deposition in the browser after executing the command.', default=False)
parser_update.add_argument('--show', action='store_true',
                           help='Show the info of the deposition after executing the command.', default=False)
parser_update.add_argument('--dump', action='store_true',
                           help='Show json for deposition after executing the command.', default=False)
parser_update.set_defaults(func=update)

parser_upload = subparsers.add_parser(
    'upload', help='Just upload files (shorthand for update id --files ...)')
parser_upload.add_argument('id', nargs='?')
parser_upload.add_argument('--bucketurl', action='store')
parser_upload.add_argument('files', nargs='*')
parser_upload.add_argument('--publish', action='store_true',
                           help='Publish the deposition after executing the command.', default=False)
parser_upload.add_argument('--open', action='store_true',
                           help='Open the deposition in the browser after executing the command.', default=False)
parser_upload.add_argument('--show', action='store_true',
                           help='Show the info of the deposition after executing the command.', default=False)
parser_upload.add_argument('--dump', action='store_true',
                           help='Show json for deposition after executing the command.', default=False)
parser_upload.set_defaults(func=upload)

parser_copy = subparsers.add_parser(
    'multiduplicate', help='Duplicates existing deposit with id multiple times, once for each file.')
parser_copy.add_argument('id', nargs=1)
parser_copy.add_argument('files', nargs='*')
parser_copy.add_argument('--publish', action='store_true',
                         help='Publish the deposition after executing the command.', default=False)
parser_copy.add_argument('--open', action='store_true',
                         help='Open the deposition in the browser after executing the command.', default=False)
parser_copy.add_argument('--show', action='store_true',
                         help='Show the info of the deposition after executing the command.', default=False)
parser_copy.add_argument('--dump', action='store_true',
                         help='Show json for deposition after executing the command.', default=False)
parser_copy.set_defaults(func=copy)

parser_newversion = subparsers.add_parser(
    'newversion', help='The newversion command creates a new version of the deposition with id, optionally providing a title / date / description / files.')
parser_newversion.add_argument('id', nargs=1)
parser_newversion.add_argument('--title', action='store')
parser_newversion.add_argument('--date', action='store')
parser_newversion.add_argument('--files', nargs='*')
parser_newversion.add_argument('--description', action='store')
parser_newversion.add_argument('--publish', action='store_true',
                               help='Publish the deposition after executing the command.', default=False)
parser_newversion.add_argument('--open', action='store_true',
                               help='Open the deposition in the browser after executing the command.', default=False)
parser_newversion.add_argument('--show', action='store_true',
                               help='Show the info of the deposition after executing the command.', default=False)
parser_newversion.add_argument('--dump', action='store_true',
                               help='Show json for deposition after executing the command.', default=False)
parser_newversion.set_defaults(func=newVersion)

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

loadConfig(args.config)
args.func(args)
