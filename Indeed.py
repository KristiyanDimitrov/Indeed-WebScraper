from bs4 import BeautifulSoup as bs
import requests
from user_agent import generate_user_agent
import soap
import urllib
from lxml import etree
import time


def get_info(page_link):
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

headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
page_link ='https://www.indeed.co.uk/jobs?q=python&l=West+Midlands'
base = 'https://www.indeed.co.uk'
page_cont = get_info(page_link)
for link in page_cont.findAll('a', attrs={'class':'jobtitle'}):
        test = get_info( base + link['href'])
        print(test)
        time.sleep(20000)
