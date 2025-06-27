import requests
from bs4 import BeautifulSoup
import json
import re
import math
from time import sleep
import subprocess

#####################################################################
# 關閉 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#####################################################################

BASEURL = 'https://ivod.ly.gov.tw/'

legislator_list = []
with open('legislators.json', 'r', encoding='utf-8') as input:
    # print(input.read())
    legislator_list = json.loads(input.read())

# print(legislator_list)

headers = {"User-Agent": "Mozilla/5.0"}
for legislator in legislator_list:

    # get max page
    url = legislator['url']
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    script_tags = soup.find_all("script", type="text/javascript")
    total, page_size, = None, None
    total_pages = None
    for script in script_tags:
        if "var total" in script.text:
            total_match = re.search(r'var total = "(.*?)";', script.string)
            page_size_match = re.search(r'var pageSize = "(.*?)";', script.string)

            if total_match and page_size_match:
                total = int(total_match.group(1))
                page_size = int(page_size_match.group(1))
                total_pages = math.ceil(total / page_size)
                break

    print('legislator:', legislator['legislator'])
    print('total_pages:', total_pages)
    sleep(1)

    # iterate through pages
    query_url = legislator['url'] + '?page='
    for i in range(1, total_pages + 1):
        page_link = requests.get(query_url + str(i), headers=headers, verify=False)
        page = BeautifulSoup(page_link.text, "html.parser")

        clips = page.find_all('ul', id="clipUl")
        
        # iterate through clips
        for clip in clips:
            
            # goto video page
            video_link = clip.find_all('a')[0].get('href')
            print(video_link)

            video_page_link = requests.get(BASEURL + video_link, headers=headers, verify=False)
            video_page = BeautifulSoup(video_page_link.text, "html.parser")

            # process video
            video_link_script = video_page.find_all('script', type="text/javascript")[1]
            video_source_link = re.search(r'readyPlayer\("([^"]+)"', video_link_script.text)
            m3u8_url = video_source_link[1]
            output_file = "legislative_meeting.mp4"
            print(m3u8_url)

            # subprocess.run([
            #     "ffmpeg",
            #     "-headers", "Referer: https://ivod.ly.gov.tw/\r\n",
            #     "-i", m3u8_url,
            #     "-c", "copy",
            #     output_file
            # ])

            # process video text
            context = video_page.find('div', class_="video-text").find_all('p')
            for con in context:
                print(con.text)
            # print(context)

            exit()
            sleep(1)
        
        exit()
        sleep(1)