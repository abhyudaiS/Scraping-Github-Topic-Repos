'''Project outline->
-We'll scrape https://github.com/topics
-We'll get a list of topics. For each topic we'll get the Topic title, topic page URL and topic description.
-For each topic we'll get top repositories from the Topic page.
-For each repository we'll get the repo name, username, stars and repo url.'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_topics_page():
        # Download the page
    topics_url = 'https://github.com/topics' 
    r = requests.get(topics_url)
        # Check successful response
    if r.status_code != 200:
        raise Exception(f'Failed to load page {topics_url}')
        # Parse using Beautiful soup
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup
soup = get_topics_page()

#We use methods from the library to get the specific tags required for our purpose. 

def get_topic_titles(soup):
    topic_title_tags = soup.find_all('p', {'class': "f3 lh-condensed mb-0 mt-1 Link--primary"})
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)
    return topic_titles
titles = get_topic_titles(soup)


def get_topic_descs(soup):
    topic_desc_tags = soup.find_all('p', {'class': "f5 color-fg-muted mb-0 mt-1"})
    topic_des = []
    for tag in topic_desc_tags:
        topic_des.append(tag.text.strip())
    return topic_des
descs = get_topic_descs(soup)


def get_topic_urls(soup):
    topic_link_tags = soup.find_all('a', {'class': "no-underline flex-1 d-flex flex-column"})
    topic_urls = []
    base_url = 'https://github.com'
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls
urls = get_topic_urls(soup)

        #The above three methods return the topic titles, description and urls of the topics in list data structure.

def scrape_topics():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception(f'Failed to load page {topics_url}')
    topics_dict = {
        'title': titles,
        'description': descs,
        'url': urls
    }
    return pd.DataFrame(topics_dict)   #We use the pandas library to create a dataframe of the extracted information and then we'll store it in the csv format.

topics_df = scrape_topics()
topics_df.to_csv('Topics.csv',index=None) 


# Get the top 25 repositories from a topic page

def get_topic_page(topic_url):
    r = requests.get(topic_url)
    if r.status_code != 200:
        raise Exception(f'Failed to load page {topic_url}')
    topic_soup = BeautifulSoup(r.text, 'html.parser')
    return topic_soup

def parse_stars_count(stars_str):
    stars_str = stars_str.strip()   
    if stars_str[-1]=='k':  #stars_str[:-1] will give everything leaving the last character
        return int(float(stars_str[:-1])*1000)
    return int(stars_str)   

def get_repo_info(h3_tag,star_tag):
    #returns all the requierd information about a repo
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url =  "https://github.com" + a_tags[1]['href']
    stars = parse_stars_count(star_tag.text.strip())
    return username, repo_name,  stars,repo_url



def get_topic_repos(topic_soup):    
    #Get the h3 tags containing repo title, repo url and username
    repo_tags  =topic_soup.find_all('h3', {'class' : "f3 color-fg-muted text-normal lh-condensed"})
    #Get star tags
    star_tags = topic_soup.find_all('span',{'class' : "Counter js-social-count"})

    topic_repos_dict = {
        'username': [],
        'repo_name':[],
        'stars':[],
        'repo_url':[]
    }

    #Get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i],star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])

    return pd.DataFrame(topic_repos_dict)


  #Defining functions to save the dataframe of the repositories info in csv format.

def scrape_topic(topic_url,topic_name):
    if os.path.exists(topic_name + '.csv'):
        print(f"The file {topic_name + '.csv'} already exists. Skipping...") #This will skip the current topic if it already exists. This will help while rescraping if it failed first time as it'll bypass all the previously scraped topics.
        return
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(topic_name + '.csv',index = None)

def scrape_topics_repos():
    print("Scraping list of topics: ")
    topics_df = scrape_topics()
    for index, row in topics_df.iterrows():
        print(f"Scraping top repositories for {row['title']}")
        scrape_topic(row['url'],row['title'])

scrape_topics_repos()
