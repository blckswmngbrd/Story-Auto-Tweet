from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from requests_oauthlib import OAuth1
import random 
import urllib.request
import requests
import json
import glob
import time
import sys
import re
import os



MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

CONSUMER_KEY = ' '
CONSUMER_SECRET = ' '
ACCESS_TOKEN = '  '
ACCESS_TOKEN_SECRET = '    '

oauth = OAuth1(CONSUMER_KEY,
  client_secret=CONSUMER_SECRET,
  resource_owner_key=ACCESS_TOKEN,
  resource_owner_secret=ACCESS_TOKEN_SECRET)

# this ANSI code lets us erase the current line
ERASE_LINE = "\x1b[2K"

class VideoTweet(object):

  def __init__(self, file_name):
    '''
    Defines video tweet properties
    '''
    self.video_filename = file_name
    self.total_bytes = os.path.getsize(self.video_filename)
    self.media_id = None
    self.processing_info = None


  def upload_init(self):
    '''
    Initializes Upload
    '''
    print('INIT')

    request_data = {
      'command': 'INIT',
      'media_type': 'video/mp4',
      'total_bytes': self.total_bytes,
      'media_category': 'tweet_video'
    }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
    media_id = req.json()['media_id']

    self.media_id = media_id

    print('Media ID: %s' % str(media_id))


  def upload_append(self):
    '''
    Uploads media in chunks and appends to chunks uploaded
    '''
    segment_id = 0
    bytes_sent = 0
    file = open(self.video_filename, 'rb')

    while bytes_sent < self.total_bytes:
      chunk = file.read(4*1024*1024)
      
      print('APPEND')

      request_data = {
        'command': 'APPEND',
        'media_id': self.media_id,
        'segment_index': segment_id
      }

      files = {
        'media':chunk
      }

      req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=oauth)

      if req.status_code < 200 or req.status_code > 299:
        print(req.status_code)
        print(req.text)
        sys.exit(0)

      segment_id = segment_id + 1
      bytes_sent = file.tell()

      print('%s of %s bytes uploaded' % (str(bytes_sent), str(self.total_bytes)))

    print('Upload chunks complete.')


  def upload_finalize(self):
    '''
    Finalizes uploads and starts video processing
    '''
    print('FINALIZE')

    request_data = {
      'command': 'FINALIZE',
      'media_id': self.media_id
    }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
    print(req.json())

    self.processing_info = req.json().get('processing_info', None)
    self.check_status()


  def check_status(self):
    '''
    Checks video processing status
    '''
    if self.processing_info is None:
      return

    state = self.processing_info['state']

    print('Media processing status is %s ' % state)

    if state == u'succeeded':
      return

    if state == u'failed':
      sys.exit(0)

    check_after_secs = self.processing_info['check_after_secs']
    
    print('Checking after %s seconds' % str(check_after_secs))
    time.sleep(check_after_secs)

    print('STATUS')

    request_params = {
      'command': 'STATUS',
      'media_id': self.media_id
    }

    req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=oauth)
    
    self.processing_info = req.json().get('processing_info', None)
    self.check_status()


  def tweet(self):
    '''
    Publishes Tweet with attached video
    '''
    value = random.randint(2019,2055)

    request_data = {
	 	 
      'status': 'YOUR STATUS',
      'media_ids': self.media_id
    }

    req = requests.post(url=POST_TWEET_URL, data=request_data, auth=oauth)
    print(req.json())




def download(path, title, mediaUrl, iterate=False, noLayerPath=None):
        print("\r" + ERASE_LINE, end="")
        print("\033[92m✔ Downloading media...\033[0m",end="", flush=True)
        urllib.request.urlretrieve(mediaUrl, path)
        print("\r" + ERASE_LINE, end="")
        print(f"\033[92m✔ Download complete: \033[0m{path}")
        print("Layer: "+ path)
        

        if iterate == True:
            print("\033[92m✔ Downloading media with no overlay...\033[0m",end="", flush=True)
            urllib.request.urlretrieve(mediaUrl.replace("embedded", "media"), noLayerPath)        
            print("\r" + ERASE_LINE, end="")
            print(f"\033[92m✔ Download complete: \033[0m{noLayerPath}")
            print("No Layer: "+noLayerPath)
        
     

def start(mapUrl):

    iterate = False
    id = re.findall(r"snap\/(.*?)\/", mapUrl)[0]
    
    API = f"https://storysharing.snapchat.com/v1/fetch/m:{id}"
    
    print("\r" + ERASE_LINE, end="")
    print("\033[92m✔ Fetching JSON data... \033[0m",end="", flush=True)
    r = requests.get(API)
    data = r.json()

    mediaType = data.get("story").get("snaps")[0].get("media").get("type")
    title = data.get("story").get("metadata").get("title")
    mediaUrl = data.get("story").get("snaps")[0].get("media").get("mediaUrl")

    os.makedirs("snapMP4", exist_ok=True)
 
   
    if "embedded" in mediaUrl:
        os.makedirs("no_layer", exist_ok=True)
        # Download the video 2 times.
        #  1. With the layer
        #  2. Without the layer
        iterate = True

    extension = mediaUrl.split("/")[-1].split(".")[-1].split("?")[0]
    
    if extension == "jpg":
        main()

    fname = f"{id}.{extension}"
    path = f"snapMP4/{fname}"
    noLayerPath = f"no_layer/{fname}"

    if "embedded" not in mediaUrl:
        os.makedirs("no_layer", exist_ok=True)
        path =  noLayerPath

    
    download(path,iterate=iterate, title=title, noLayerPath=noLayerPath, mediaUrl=mediaUrl)
    

def main():
        #Set headless options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    #options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
        
    driver.get('social media story url location')   
    time.sleep(10)
    driver.find_element_by_xpath('xpath of entryconfirmation').click()
    time.sleep(15)
    driver.find_element_by_xpath('xpath of video location').click()
    time.sleep(5)
    mapUrl = driver.current_url
    print("MapUrl:" + mapUrl)
    time.sleep(5)
    start(mapUrl)
    time.sleep(180)
    driver.close()
    list_of_files = glob.glob('/filepath/*') 
    latest_file = max(list_of_files, key=os.path.getctime)
    mp4File =  latest_file
    videoTweet = VideoTweet(mp4File)
    videoTweet.upload_init()
    videoTweet.upload_append()
    videoTweet.upload_finalize()
    videoTweet.tweet()
    wasteSnaps = glob.glob('/filepath/')		
    for f in list_of_files:
         os.remove(f)
    for s in wasteSnaps:
         os.remove(s)
    
    


if __name__=="__main__":
    main()
