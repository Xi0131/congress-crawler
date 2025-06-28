import requests
from bs4 import BeautifulSoup
import json
import re
import math
from time import sleep
import subprocess
import os

#####################################################################
# 關閉 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#####################################################################

BASEURL = 'https://ivod.ly.gov.tw'

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
    for i in range(2, total_pages + 1):
        print('page:', i)
        page_link = requests.get(query_url + str(i), headers=headers, verify=False)
        page = BeautifulSoup(page_link.text, "html.parser")

        clips = page.find_all('ul', id="clipUl")
        
        # iterate through clips
        for clip in clips:
            
            # process clip info
            clip_info = clip.find('div', class_="clip-list-text")
            title = clip_info.find('h5').text
            term = re.search(r"第(\d+)屆\s+第(\d+)會期\s*?主辦單位：\s*(\S+)", title)[1]
            session = re.search(r"第(\d+)屆\s+第(\d+)會期\s*?主辦單位：\s*(\S+)", title)[2]
            organizer = re.search(r"第(\d+)屆\s+第(\d+)會期\s*?主辦單位：\s*(\S+)", title)[3]
            
            context = clip_info.find_all('p')
            legislator_name = re.search(r'委員：\s*(.+)', context[0].text)[1]
            speaking_time = re.search(r'委員發言時間：\s*(.+)', context[1].text)[1]
            video_length = re.search(r'影片長度：\s*(.+)', context[2].text)[1]
            meeting_time = re.search(r'會議時間：\s*(.+)', context[3].text)[1]
            meeting_name = re.search(r'會議名稱：\s*(.+)', context[4].text)[1]
            
            clip_links = context[5].find_all('a')
            gazette_link, record_sublink, related_info = '', '', ''
            for a in clip_links:
                if a.text == '公報連結':
                    gazette_link = a.get('href')
                elif a.text == '發言紀錄':
                    record_sublink = re.search(r"window\.open\('([^']+)'", a.get('href'))[1]
                elif a.text == '會議相關資料':
                    meeting_info = a.get('href')
            
            video_data = {
                "主辦單位" : organizer,
                "會期" : f'第{term}屆第{session}會期',
                "委員名稱" : legislator_name,
                "委員發言時間" : speaking_time,
                "影片長度" : video_length,
                "會議時間" : meeting_time,
                "會議名稱" : meeting_name,
                "公報連結" : gazette_link,
                "發言紀錄" : BASEURL + record_sublink,
                "會議相關資料" : meeting_info
            }
            print(video_data)
            
            # set paths
            legislator_dir      = f'委員資料夾/{legislator_name}'
            video_dir           = f'{legislator_dir}/{session}_{legislator_name}_{meeting_time.replace(' ', '_').replace(':', '')}'
            video_output_file   = f"{video_dir}/videoClip.mp4"
            json_output_file    = f"{video_dir}/metaData.json"
            record_output_file  = f"{video_dir}/record.txt"
            
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)

            # goto video page
            video_link = clip.find_all('a')[0].get('href')
            print(video_link)
            video_page_link = requests.get(BASEURL + video_link, headers=headers, verify=False)
            video_page = BeautifulSoup(video_page_link.text, "html.parser")
            
            # process video
            video_link_script = video_page.find_all('script', type="text/javascript")[1]
            video_source_link = re.search(r'readyPlayer\("([^"]+)"', video_link_script.text)
            m3u8_url = video_source_link[1]
            print(m3u8_url)

            subprocess.run([
                "ffmpeg",
                "-headers", "Referer: https://ivod.ly.gov.tw/\r\n",
                "-i", m3u8_url,
                "-c", "copy",
                video_output_file
            ])

            with open(json_output_file, 'w', encoding='utf-8') as jout:
                jout.write(json.dumps(video_data, ensure_ascii=False, indent=4))

            sleep(1)
            
            if record_sublink != '':
                record_link = requests.get(BASEURL + record_sublink, headers=headers, verify=False)
                record = BeautifulSoup(record_link.text, "html.parser")
                print(record)
                with open(record_output_file, 'w', encoding='utf-8') as rout:
                    rout.write(record.text)

            sleep(1)
        
        sleep(1)