import requests
import os
import urllib2
import os, sys, tarfile
import shutil
import logging

logger = logging.getLogger(__name__)


# This is a nifty little script which uploads our vocabulary file
# we have created of words we want to recognize and then downloads
# the created vocabulary from the sphinx site using their form
# post. 

URL = "http://www.speech.cs.cmu.edu/cgi-bin/tools/lmtool/run"
HEARING_FILE_ROOT = os.path.normpath(os.path.dirname(__file__) )
VOCABULARY_FILE = HEARING_FILE_ROOT + "/vocabulary.txt"
DOWNLOADED_FILE = HEARING_FILE_ROOT + "/sphinx.tgz"
EXTRACTED_DIRECTORY = HEARING_FILE_ROOT + "/sphinx_vocabulary/"

def updateVocabulary( ):

    try:
        #Do the request to download the file
        __downloadSphinxFile( VOCABULARY_FILE, DOWNLOADED_FILE )
    except Exception as e:
        logger.error("Tried to update Sphinx voice files but was not successful: " + str(e))
        # Return because we hopefully already have old ones
        return

    # Delete our old ones and remake the directory
    if os.path.exists(EXTRACTED_DIRECTORY):
        shutil.rmtree( EXTRACTED_DIRECTORY )

    os.makedirs(EXTRACTED_DIRECTORY)

    # Extract it to the correct location 
    __extract( DOWNLOADED_FILE, EXTRACTED_DIRECTORY )

    # Remove the TAR to clean up
    os.remove( DOWNLOADED_FILE )

    __removeDateToCleanCommit( EXTRACTED_DIRECTORY + '/vocab.lm' )



def __extract(tar_url, extract_path='.'):
    '''
    Simply extracts the TAR to the defined location

    '''
    #print tar_url
    tar = tarfile.open(tar_url, 'r')
    for item in tar:
        tar.extract(item, extract_path)
        # Now we want to rename them to be vocab.* because it downloads
        # a different name each time
        prefix = item.name.split('.')[0]
        os.rename(extract_path + "/" + item.name, extract_path + "/vocab." + item.name.split('.')[1] )

        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])



def __downloadSphinxFile( vocabularyFilePath, downloadFilePath ):
    '''
    Does a request to download all the data for each 

    '''
    with open( vocabularyFilePath ) as f:
        txt = f.read()

    #print txt
    files = {"formtype":"", "corpus": txt }
    response = requests.post(URL, files=files)

    #response = requests.post(URL, urllib.urlencode({'formtype':'', 'files':{'corpus':txt} }) )
    for line in response.content.split('\n'):
        if ".tgz" in line:
            #print("found line with URL: " +line )
            url = line.split('"')[1]

            if ".tgz" in url:
                break

    response = urllib2.urlopen(url)
    zippedFile = response.read()

    with open( downloadFilePath, 'w' ) as f:
        f.write( zippedFile )



def __removeDateToCleanCommit( path ):
    '''
    Every time we request a new file, it changes the date so GIT thinks we need to
    recommit it. This will remove that date code.
    '''
    with open( path, 'r') as f:
        contents = f.read()

    #logger.debug(contents)

    with open( path, 'w') as f:
        lines = contents.split('\n')

        for line in lines:
            #logger.debug(">> " + line)
            # Get rid of the date element
            if 'Language model created by' in line:
                shorterLine = line.split('on')[0]
                logger.debug("Found time line and removed: " + line + " " + shorterLine)
                line = shorterLine
            f.write( line + "\n" )


