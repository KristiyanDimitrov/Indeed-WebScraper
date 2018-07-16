from bs4 import BeautifulSoup as bs
import requests
from user_agent import generate_user_agent
import soap
import urllib
from lxml import etree
import time


def get_all_jobs(page_link):
    try:
        page_response = requests.get(page_link, timeout=10)
        if page_response.status_code == 200:
            #page_content = BeautifulSoup(page_response.content, "html.parser")
            page_content = bs(urllib.urlopen(page_link, "lxml"))
        else:
            print ("Failed!")
            print(page_response.status_code)
    except requests.Timeout as e:
        print("It is time to timeout")
        print(str(e))
    except:
        print(" Unknown exception!")
    if 'page_content' in locals():
        return page_content
    else:
        return None

def get_job():
    page_cont = get_all_jobs(page_link)
    for link in page_cont.findAll('a', attrs={'class': 'jobtitle'}):
        links = get_all_jobs(base + link['href'])
        yield links

headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
page_link ='https://www.indeed.co.uk/jobs?q=python&l=West+Midlands'
base = 'https://www.indeed.co.uk'

jobs= get_job()
jobs_text = {}
index = 0
summary = ''

for job in jobs:

    for item in job.findAll('span', attrs={'class': 'summary'}):
        for element in item:
            try:
                summary += element.text
                print(element.text)
            except Exception as e:
                print("Err passed by TRY: " + str(e))
                print("<<<<<<<<<<<<<<<<<<")
                print("RUN TIME ERR due to unexpected element")
                print(">>>>>>>>>>>>>>>>>>>>>")
                print("Type of element :" + str(type(element)))
                if str(type(element)) == "<class 'bs4.element.Tag'>":
                    print("Passing element:")
                    print(element)
                else:
                    summary += element
                    print(element)
    temp = index
    jobs_text[temp] = summary
    index += 1
    print("Entry recorded!")
    break

print(jobs_text[0])
print(jobs_text[1])
time.sleep(20000)

