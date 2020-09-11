import requests
from bs4 import BeautifulSoup
from google_sheets import harvest_sheet_tsv
import logging
import csv
from datetime import date
import pandas as pd
from metrics import write_metric


def harvest_business_operations(path):
    """Harvest Business Operations Spreadsheet"""

    logging.info("harvest_business_operations")
    # harvest_social_media(path)
    harvest_sheet_tsv(path=path,
                      name="business_operations",
                      sheet_id='1TXGcNBAPYmAgITwJ7dBAP2cB3Kkfigss_Kcr2A6jwUE',
                      range_name='Sponsored Research!A:I',
                      columns=[])


def aggregate_bo(path, tsv):
    df = pd.read_csv(path + tsv + ".tsv", delimiter="\t")
    df1 = df[df["Group"] == "Sponsored Research Administration"].iloc[:, 0:7]
    df2 = df[df["Group"] != "Sponsored Research Administration"].iloc[:, 0:7]

    update_date = df[df["Updated"].isnull() == False]["Updated"][0]
    pd.DataFrame({"Department": ["Business Operations"], "Last Update": update_date}).to_csv(path + "update_dates.tsv",
                                                                                             sep='\t', index=False)

    metric_df = df[df["Homepage"].isnull() == False].values.tolist()[0]

    df1.to_csv(path + "sponsored_research_administration.tsv", sep='\t', index=False)
    df2.to_csv(path + "finance_and_administration.tsv", sep='\t', index=False)

    write_metric(path=path, group=metric_df[0], metric=metric_df[1],
                 title=metric_df[1],
                 value=metric_df[6], unit=metric_df[5],
                 icon=metric_df[2], color=metric_df[4],
                 url=metric_df[3])


def harvest_social_media(path):
    logging.info("Harvesting Social Media")

    collection_name = "social_media"
    now = date.today().strftime('%Y-%m-%d')

    # Write social_media_all once a day to prevent double records
    with open(path + collection_name + "_all.tsv", 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for r in reader:
            if r[0] == now:
                logging.info("Social media already harvested")
                return
    # Twitter --------------
    logging.info("Harvesting Twitter")
    domain = 'https://twitter.com/IQSS'
    data = requests.get(domain)

    soup = BeautifulSoup(data.text, 'html.parser')

    soup.find_all(class_='ProfileNav-item--followers')

    followers = soup.find(class_='ProfileNav-item--followers').find_all('span', class_='ProfileNav-value')[
        0].text.strip()

    followers = int(followers.replace(",", ""))

    tweets = soup.find(class_='ProfileNav-item--tweets').find('span',
                                                              class_='ProfileNav-value').text.strip()
    tweets = int(tweets.replace(",", ""))

    # TODO: check if records can be retrieved before writing to the database

    posts = [['date', 'group', 'metric', 'title', 'value', 'unit', 'icon', 'color', 'url'],
             [now, 'Social Media', 'Twitter Followers', 'Twitter', followers, 'Total Followers', 'fa fa-heart',
              'light-blue',
              "https://twitter.com/IQSS"],
             [now, 'Social Media', 'Twitter Tweets', 'Twitter', tweets, 'Total Tweets', 'fab fa-twitter', 'light-blue',
              "https://twitter.com/IQSS"]]

    # Facebook --------------------
    logging.info("Harvesting Facebook")
    domain = 'https://www.facebook.com/iqssharvard'
    data = requests.get(domain)

    soup = BeautifulSoup(data.text, 'html.parser')

    divs = soup.find_all('div')

    fb_follow = ''
    fb_like = ''

    for d in divs:
        if d.text.endswith('like this'):

            if fb_like == '':
                fb_like = d.text.split(' ')[0]

        if d.text.endswith('follow this'):
            if fb_follow == '':
                fb_follow = d.text.split(' ')[0]

    fb_like = int(fb_like.replace(",", ""))
    fb_follow = int(fb_follow.replace(",", ""))

    posts.append([now, 'Social Media', 'Facebook Likes', 'Facebook', fb_like, 'Total Likes', 'fa fa-thumbs-up', 'blue',
                  'https://www.facebook.com/iqssharvard'])
    posts.append(
        [now, 'Social Media', 'Facebook Followers', 'Facebook', fb_follow, 'Total Followers', 'fab fa-facebook-square',
         'blue', 'https://www.facebook.com/iqssharvard'])

    if len(posts) == 5:  # 4 records including header
        with open(path + collection_name + ".tsv", 'w') as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            for row in posts:
                writer.writerow(row)

        with open(path + collection_name + "_all.tsv", 'a') as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            for row in range(1, len(posts)):
                writer.writerow(posts[row])

    else:
        logging.error('Could not load Facebook and Twitter stats (%s records)', str(len(posts) - 1))
        logging.error('')
