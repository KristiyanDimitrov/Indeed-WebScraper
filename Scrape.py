import soap, urllib, requests, pymongo, time, pika, json, datetime
from bs4 import BeautifulSoup as bs
from user_agent import generate_user_agent
from lxml import etree
from pymongo import MongoClient
from itertools import izip


# Try extracting the 'page_link' HTML and return it. Exceptions covered
def get_all_jobs(page_link):

    try:
        page_response = requests.get(page_link, timeout=10)
        if page_response.status_code == 200:
            page_content = bs(urllib.urlopen(page_link), "html.parser")
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

# Get all jobs HTML on the main page in a generator to save memory.
def get_job(page_cont):
    jobs_1 = page_cont.findAll('a', attrs={'class': 'jobtitle'})
    jobs_2 = page_cont.findAll('a', attrs={'class': 'turnstileLink'})
    jobs = jobs_1 + jobs_2
    for link in jobs :
        links = get_all_jobs(base + link['href'])
        yield links, link['href']

# Get job information
def get_job_info(jobs, pageN, link):
    summary = ''
    readings = []

    for job in jobs:
        if job is None:
            continue

        for item in job.findAll('span', attrs={'class': 'summary'}):
            for element in item:
                try:
                    summary += element.text
                except Exception as e:
                    if str(type(element)) == "<class 'bs4.element.Tag'>":
                        print("Passing element:")
                    else:
                        summary += element
        job_title = job.find('b', attrs={'class': 'jobtitle'})
        date = job.find('span', attrs={'class': 'date'})
        if job_title is None:
            continue
        else:
            job_title = job_title.text
            date = date.text
        read = {
            "page_number": pageN,
            "link" : (base + link[len(readings)-1]),
            "title": job_title,
            "summary": summary.replace("\n", " "),
            'post_date': date,
            'record_date': datetime.datetime.today()
        }
        readings.append(read)
        summary = ""

        # Make sure the file name is readable and valid.
        if save_file is True:
            try:
                name = str(read['title'])
                name = unicode(name, 'utf-8')
                name = name.replace(" ", "_").replace("/", "").replace("|", "").replace("&", "")
            except UnicodeEncodeError:
                name = "name_error"
            job_name = "./jobs_html/" + name.encode('utf-8') + '.html'
            with open(job_name, 'a') as the_job:
                the_job.write(str(job))
            print("Page source file for job(" + str(job_name) + ") created!")

    return readings

def store_readings(results):
    user = 'mongodb://KristiyanDimitrov:*******@ds247191.mlab.com:47191/jobs_info'
    client = MongoClient(user)
    db = client.jobs_info
    collection = db.jobs

    # Add all the found jobs by checking if they are in the db and updating it to avoid dublicates
    stored_num = 0
    for result in results:
        check = collection.find_one({"title": result['title']})
        if check is None:
            collection.update(result, result, upsert=True)
            queue_send(result['title'])
            stored_num += 1
            try:
                print("Send to queue for :" + result['title'])
            except:
                # if there are any encoding problems
                print("Send to queue for : ????????")

    print(str(stored_num) + " jobs stored/updated!")

def queue_send(record):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Create queue/ make sure it exsists, not a problem if done multiple times
    # When re-declaring, adding durable will raise an error
    channel.queue_declare(queue='task_queue', durable=True)

    # Feed queue
    channel.basic_publish(exchange='',
                          routing_key="task_queue",
                          body=json.dumps(record),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    """
    Marking messages as persistent doesn't fully guarantee that a message won't be lost. Although it tells RabbitMQ to save the message
    to disk, there is still a short time window when RabbitMQ has accepted a message and hasn't saved it yet. 
    Also, RabbitMQ doesn't do fsync(2) for every message -- it may be just saved to cache and not really written to the disk.
    The persistence guarantees aren't strong, but it's more than enough for our simple task queue. 
    If you need a stronger guarantee then you can use publisher confirms.
    """

    # Close the connection
    connection.close()

def main():
    global base, page_link, headers, next_page, save_file
    numberOfPages_toRead = 1
    # 'True' is you need to save the html pages
    save_file = False
    # Use a header to identify as a user against bot defence
    headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
    page_link ='https://www.indeed.co.uk/jobs?q=python&l=West+Midlands'
    base = 'https://www.indeed.co.uk'
    # Keep track of the page
    next_page = 1
    readings = []

    # Traverse the number of pages requested
    while next_page <= numberOfPages_toRead:
        print("\n\nNavigate to page: " + str(next_page))
        print(page_link)

        # Get page HTML
        page_cont = get_all_jobs(page_link)
        # Get a job from the main HTML and its link from a generator object. Using izip to handle 2 items in a generator.
        jobs, link = izip(*get_job(page_cont))
        # Get job data
        readings += get_job_info(jobs, next_page, link)


        # Constructing next page link
        page_link = ("https://www.indeed.co.uk/jobs?q=python&l=West+Midlands&start=" + str(next_page*10))
        next_page += 1

        # Store page for testing
        if save_file is True:
            page_name = './pages_html/page_' + str(next_page-1) +'.html'
            with open(page_name, 'a') as the_file:
                the_file.write(str(page_cont))
            print("Page source file for page(" + str(next_page-1) + ") created or updated!" )

        store_readings(readings)
        readings = []




if __name__ == "__main__":
    main()


