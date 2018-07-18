import soap, urllib, requests
from bs4 import BeautifulSoup as bs
from user_agent import generate_user_agent
from lxml import etree
import time


def get_all_jobs(page_link):
    try:
        page_response = requests.get(page_link, timeout=10)
        if page_response.status_code == 200:
            page_content = bs(urllib.urlopen(page_link))
        else:
            print ("Failed!")
            print(page_response.status_code)
    except requests.Timeout as e:
        print("It is time to timeout")
        print(str(e))
    except:
        print(" Unknown exception!")
    if 'page_content' in locals():
        #next_page = page_content.find('div', attrs={'class': 'pagination'})
        #print(next_page)
        #time.sleep(20000)
        #next_page = next_page.find_last('a')
        return page_content
    else:
        return None

def get_job(page_cont):
    jobs_1 = page_cont.findAll('a', attrs={'class': 'jobtitle'})
    jobs_2 = page_cont.findAll('a', attrs={'class': 'turnstileLink'})
    jobs = jobs_1 + jobs_2
    for link in jobs :
        links = get_all_jobs(base + link['href'])
        yield links

def get_job_info(jobs, pageN):
    summary = ''
    readings = []
    for job in jobs:

        for item in job.findAll('span', attrs={'class': 'summary'}):
            for element in item:
                try:
                    summary += element.text
                    # print(element.text)
                except Exception as e:
                    #print("Error passed by TRY: " + str(e))
                    #print("Type of element :" + str(type(element)))
                    if str(type(element)) == "<class 'bs4.element.Tag'>":
                        print("Passing element:")
                        #print(element)
                    else:
                        summary += element
                        #print(element)
        job_title = job.find('b', attrs={'class': 'jobtitle'})
        if job_title is None:
            continue
        else:
            job_title = job_title.text
        read = {
            'page_number': pageN,
            'title': job_title,
            'summary': summary
        }
        readings.append(read)
        summary = ""
        print("Entry recorded!")

    time.sleep(4)
    return readings


numberOfPages_toRead = 3
headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
page_link ='https://www.indeed.co.uk/jobs?q=python&l=West+Midlands'
base = 'https://www.indeed.co.uk'
next_page = 1


while next_page < numberOfPages_toRead:
    page_cont = get_all_jobs(page_link)
    jobs= get_job(page_cont)
    readings = get_job_info(jobs, next_page)

    # Constructing next page link
    page_link = ("https://www.indeed.co.uk/jobs?q=python&l=West+Midlands&start=" + str(next_page*10))
    next_page += 1

    # Print found job titles
    for read in readings:
        print(read['title'])
    time.sleep(15)

    # Store page to testing
    page_name = 'page_' + str(next_page-1) +'.html'
    with open(page_name, 'a') as the_file:
        the_file.write(str(page_cont))
    print("Check the file!")

    print("Navigate to page: " + str(next_page))
    print(page_link)


#for reading in readings:
#    print(reading)
#    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
#    print('>>>>>>>>>>>>>>>>>>>' + reading['title'] + '>>>>>>>>>>>>>>>>>')
#    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

