import requests
from bs4 import BeautifulSoup
import json
import re
import math
from time import sleep
import subprocess
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--name', type=str, help='Skip until this legislator')
parser.add_argument('--page', type=int, help='Skip until this legislator')
args = parser.parse_args()
start_leg = args.name
start_page = args.page
skip_leg = True
skip_page = True

#####################################################################
# 關閉 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#####################################################################

def is_complete_mp4(file_path):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True,
            text=True
        )
        duration_str = result.stdout.strip()
        duration = float(duration_str)
        return duration > 0
    except Exception:
        # ffprobe failed: likely no moov atom or corrupt file
        return False

BASEURL = 'https://ivod.ly.gov.tw'

legislator_list = []
with open('legislators.json', 'r', encoding='utf-8') as input:
    legislator_list = json.loads(input.read())

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

    if start_leg == None:
        skip_leg = False
        skip_page = False
    elif start_leg == legislator['legislator']:
        skip_leg = False
        if start_page == None:
            skip_page = False
    elif skip_leg == True:
        print('skipping')
        continue

    print('total_pages:', total_pages)
    sleep(1)

    # iterate through pages
    i = 1
    query_url = legislator['url'] + '?page='
    while i <= total_pages + 1:
        if skip_page == True:
            i = start_page - 1
            print('skip until page', i)
            skip_page = False

        print('page:', i)
        page_link = requests.get(query_url + str(i), headers=headers, verify=False)
        page = BeautifulSoup(page_link.text, "html.parser")

        clips = page.find_all('ul', id="clipUl")
        
        # iterate through clips
        for clip in clips:
            
            # process clip info
            clip_info = clip.find('div', class_="clip-list-text")
            title = clip_info.find('h5').text
            term        = re.search(r"第(\d+)屆\s+第(\d+)會期\s*?主辦單位：\s*(\S+)", title)[1]
            session     = re.search(r"第(\d+)屆\s+第(\d+)會期\s*?主辦單位：\s*(\S+)", title)[2]
            organizer   = re.search(r"第(\d+)屆\s+第(\d+)會期\s*?主辦單位：\s*(\S+)", title)[3]
            
            context = clip_info.find_all('p')
            legislator_name = re.search(r'委員：\s*(.+)', context[0].text)[1]
            speaking_time   = re.search(r'委員發言時間：\s*(.+)', context[1].text)[1].replace(':', '').replace(' ', '')
            clip_length     = re.search(r'影片長度：\s*(.+)', context[2].text)[1].replace(':', '')
            meeting_time    = re.search(r'會議時間：\s*(.+)', context[3].text)[1].replace(' ', '_').replace(':', '')
            meeting_name    = re.search(r'會議名稱：\s*(.+)', context[4].text)[1]
            meeting_info    = ''

            clip_links = context[5].find_all('a')
            gazette_link, record_sublink, related_info = '', '', ''
            for a in clip_links:
                if a.text == '公報連結':
                    gazette_link = a.get('href')
                elif a.text == '發言紀錄':
                    record_sublink = re.search(r"window\.open\('([^']+)'", a.get('href'))[1]
                elif a.text == '會議相關資料':
                    meeting_info = a.get('href')
            
            clip_data = {
                "主辦單位" : organizer,
                "會期" : f'第{term}屆第{session}會期',
                "委員名稱" : legislator_name,
                "委員發言時間" : speaking_time,
                "影片長度" : clip_length,
                "會議時間" : meeting_time,
                "會議名稱" : meeting_name,
                "公報連結" : gazette_link,
                "發言紀錄" : BASEURL + record_sublink,
                "會議相關資料" : meeting_info
            }
            print('clip data:', clip_data)
            
            # set paths
            dir_suffix          = re.match(r'(\d{6})-(\d{6})', speaking_time)[1]
            legislator_dir      = f'委員資料夾/{legislator_name}'
            clip_dir            = f'{legislator_dir}/第{term}屆第{session}會期_{legislator_name}_{meeting_time}_{dir_suffix}'
            clip_output_file    = f"{clip_dir}/videoClip.mp4"
            json_output_file    = f"{clip_dir}/metaData.json"
            record_output_file  = f"{clip_dir}/record.txt"
            
            if not os.path.exists(clip_dir):
                os.makedirs(clip_dir)

            if not os.path.exists(json_output_file):
                with open(json_output_file, 'w', encoding='utf-8') as jout:
                    jout.write(json.dumps(clip_data, ensure_ascii=False, indent=4))
            
            if os.path.exists(record_output_file):
                continue
            
            if record_sublink != '' and not os.path.exists(record_output_file):
                record_link = requests.get(BASEURL + record_sublink, headers=headers, verify=False)
                record = BeautifulSoup(record_link.text, "html.parser")
                with open(record_output_file, 'w', encoding='utf-8') as rout:
                    rout.write(record.text)
            elif not os.path.exists(clip_output_file) or not is_complete_mp4(clip_output_file):
                # goto clip page
                print('page:', i)
                print('record link not found, download clip instead')
                clip_page_link = clip.find_all('a')[0].get('href')
                print('clip page link:', clip_page_link)
                clip_page_link = requests.get(BASEURL + clip_page_link, headers=headers, verify=False)
                clip_page = BeautifulSoup(clip_page_link.text, "html.parser")
                sleep(3)
            
                # process clip
                clip_link_script = clip_page.find_all('script', type="text/javascript")[1]
                clip_source_link = re.search(r'readyPlayer\("([^"]+)"', clip_link_script.text)
                m3u8_url = clip_source_link[1]
                print('clip link:', m3u8_url)

                subprocess.run([
                    "ffmpeg",
                    "-headers", "Referer: https://ivod.ly.gov.tw/\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n",
                    "-re",
                    "-i", m3u8_url,
                    "-c", "copy",
                    "-y",
                    clip_output_file
                ])
                sleep(10)
            else:
                print('clip or record exists, skipping')
            
        
        sleep(5)
        i += 1
