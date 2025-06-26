import requests
from bs4 import BeautifulSoup
import json

# headers = {
#     'User-Agent': 'Mozilla/5.0'
# }
# url = 'https://ivod.ly.gov.tw/Demand?targetSession=current'
# response = requests.get(url, headers=headers, verify=False)
# with open('legislator_list.html', 'w', encoding='utf-8') as tmp:
#     tmp.write(response.text)
# soup = BeautifulSoup(response.text, 'html.parser')

# to read from local html
response = ''
with open('legislator_list.html', 'r', encoding='utf-8') as input:
    response = input.read()
soup = BeautifulSoup(response, 'html.parser')

legislators_lists = soup.find_all('ul', 'table-list')

legislators_data = []
for legislators_list in legislators_lists:
    legislators = legislators_list.find_all('li')
    for legislator in legislators:
        legislators_data.append({
            "legislator": legislator.text,
            "url": legislator.find('a').get('href')
        })
        print(f'- {legislator.text}: {legislator.find('a').get('href')}')

with open('legislators.json', 'w', encoding='utf-8') as output_file:
    json.dump(legislators_data, output_file, ensure_ascii=False, indent=4)