# Read this first https://developers.zenodo.org/#quickstart-upload

import requests
import sys
import re
import webbrowser

params = {'access_token': 'YOUR_ACCESS_TOKEN'}

def getData(ORIGINAL_DEPOSIT_ID):
    # Fetch the original deposit metadata
    res = requests.get(
        'https://zenodo.org/api/deposit/depositions/{}'.format(ORIGINAL_DEPOSIT_ID),
        params=params)
    if res.status_code != 200:
        sys.exit('Error in getting ORIGINAL_DEPOSIT')        
    metadata = res.json()['metadata']
    return metadata

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
    print('\tNew deposit for {0} created; bucket_url {1}'.format(journal_filepath, bucket_url))
    webbrowser.open_new_tab(deposit_url)


if len(sys.argv)<2:
    print("Usage: zenodo-cli <action> ... ")
    print("       zenodo-cli get deposit_id")
    print("       zenodo-cli create file1.json [file2.json [file3.json ...]]")
    print("       zenodo-cli duplicate original_deposit_id [title]")
    print("       zenodo-cli copy original_deposit_id file1.pdf [file2.pdf [file3.pdf ...]]")
    sys.exit('ERROR: Too few arguments.');

action = sys.argv[1]

if action == "get":
    # Get and print deposit metadata from deposit id provided as arguments.
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    metadata = getData(ORIGINAL_DEPOSIT_ID)
    print(metadata)

if action == "create":
    # Create new deposits from metadata files (json) provided as arguments.
    JSON_FILES = sys.argv[2:len(sys.argv)]

    metadata = getData(ORIGINAL_DEPOSIT_ID)
    del metadata['doi']
    # Do not allocate a DOI
    del metadata['prereserve_doi']

    # Create new deposits based on the provided metadata
    for json_filepath in JSON_FILES:
        print('Processing: '+json_filepath)
        replaced = re.sub('^.*\/', '', json_filepath)
        print('\tfilename: '+replaced)
        file = open(json_filepath,mode='r')
        metadata = file.read()
        file.close()
        response_data = createRecord(metadata)

    
if action == "duplicate":
    # Arguments: ORIGINAL_DEPOSIT_ID STRING_TITLE
    # Create a new record with the metadata of the record ORIGINAL_DEPOSIT_ID, but with the title replaced by STRING_TITLE.
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    TITLES = sys.argv[3:len(sys.argv)]
    metadata = getData(ORIGINAL_DEPOSIT_ID)
    del metadata['doi']  # remove the old DOI
    metadata['prereserve_doi'] = True

    # This needs to be fixed to allow multiple titles to create multiple records
    if TITLES:
        metadata['title'] = TITLES[0]
    
    response_data = createRecord(metadata)
    
if action == "copy":
    # Arguments: ORIGINAL_DEPOSIT_ID FILE1 FILE2
    # Create a new record with the metadata of the record ORIGINAL_DEPOSIT_ID, and attach FILE1. Repeat for FILE2.
    ORIGINAL_DEPOSIT_ID = sys.argv[2]
    # Modify the list accordingly...
    JOURNAL_FILES = sys.argv[3:len(sys.argv)]

    metadata = getData(ORIGINAL_DEPOSIT_ID)
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