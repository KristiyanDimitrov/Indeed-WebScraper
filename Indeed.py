import soap, urllib, requests
from bs4 import BeautifulSoup as bs
from user_agent import generate_user_agent
from lxml import etree


def get_all_jobs(page_link):
    try:
        page_response = requests.get(page_link, timeout=10)
        if page_response.status_code == 200:
            page_content = bs(urllib.urlopen(page_link, "xml"))
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

def get_job(page_cont):
    for link in page_cont.findAll('a', attrs={'class': 'jobtitle'}):
        links = get_all_jobs(base + link['href'])
        yield links

def get_job_info(jobs):
    summary = ''
    readings = []
    for job in jobs:

        for item in job.findAll('span', attrs={'class': 'summary'}):
            for element in item:
                try:
                    summary += element.text
                    # print(element.text)
                except Exception as e:
                    print("Error passed by TRY: " + str(e))
                    print("Type of element :" + str(type(element)))
                    if str(type(element)) == "<class 'bs4.element.Tag'>":
                        print("Passing element:")
                        # print(element)
                    else:
                        summary += element
                        print(element)
        job_title = job.find('b', attrs={'class': 'jobtitle'})
        if job_title is None:
            continue
        else:
            job_title = job_title.text
        read = {
            'title': job_title,
            'summary': summary
        }
        readings.append(read)
        summary = ""
        print("Entry recorded!")
    return readings



headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
page_link ='https://www.indeed.co.uk/jobs?q=python&l=West+Midlands'
base = 'https://www.indeed.co.uk'
page_cont = get_all_jobs(page_link)

jobs= get_job(page_cont)
readings = get_job_info(jobs)

for reading in readings:
    print(reading)
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print('>>>>>>>>>>>>>>>>>>>' + reading['title'] + '>>>>>>>>>>>>>>>>>')
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

