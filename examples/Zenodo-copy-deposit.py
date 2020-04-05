# Read this first https://developers.zenodo.org/#quickstart-upload

import requests
import sys
import re
import webbrowser

params = {'access_token': 'REPLACE-ME'}


if len(sys.argv)<2:
    print("Usage: script.py original_deposit_id file1.pdf [file2.pdf [file3.pdf ...]]")
    sys.exit('ERROR: Too few arguments.');
    
# Modify the list accordingly...
JOURNAL_FILES = sys.argv[2:len(sys.argv)]


# Fetch the original deposit metadata
ORIGINAL_DEPOSIT_ID = sys.argv[1]
res = requests.get(
    'https://zenodo.org/api/deposit/depositions/{}'.format(ORIGINAL_DEPOSIT_ID),
    params=params)
if res.status_code != 200:
    sys.exit('Error in getting ORIGINAL_DEPOSIT')
    
metadata = res.json()['metadata']
del metadata['doi']  # remove the old DOI
del metadata['prereserve_doi']

# Create new deposits based on the original metadata
for journal_filepath in JOURNAL_FILES:
    # Notify user of file to be uploaded.
    print('Processing: '+journal_filepath)
    replaced = re.sub('^.*\/', '', journal_filepath)
    print('\tfilename: '+replaced)

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
    print('\tNew deposit for {0} created at: {1}'.format(journal_filepath, deposit_url))

    # File upload    
    print('\tUploading file.')
    # Get bucket_url
    bucket_url = response_data['links']['bucket']
    # Upload file.
    with open(journal_filepath, 'rb') as fp:
        res = requests.put(bucket_url + '/' + replaced, data=fp, params=params)
    if res.status_code != 200:
        sys.exit('Error in creating file upload.')
    # notify user
    print('\tUpload successful.')

    # open deposit url so that the user can edit.
    webbrowser.open_new_tab(deposit_url)
