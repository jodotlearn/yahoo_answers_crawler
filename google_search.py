# encoding: utf-8
import json
import time

from bs4 import BeautifulSoup
from jsoncomment import JsonComment
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


def main():
    mongodb_uri = 'mongodb://udiclab:udiclab@127.0.0.1/yahoo_answers'
    client = MongoClient(mongodb_uri, 10017)
    db = client['yahoo_answers']
    collection_question = db['qs']
    collection_googleresult = db['gr']


    searchbox_id = "lst-ib"
    chrome_driver = '/Users/jo/Documents/workspaces/python/yahoo_answers_crawler/driver/chromedriver'
    browser = webdriver.Chrome(chrome_driver)
    base_url = "https://www.google.com.tw"
    browser.get(base_url)
    result_list = []
    for q in collection_question.find({'isDeal':'N'}):
        searchbox = browser.find_element_by_id(searchbox_id)
        searchbox.clear()
        searchbox.send_keys(q['question'])
        searchbox.send_keys(Keys.ENTER)
        time.sleep(3)
        result = browser.find_elements_by_class_name("rc")
        # summary = browser.find_elements_by_class_name("st")
        for r in result:
            try:
                title = r.find_element_by_class_name("r")
                summary = r.find_element_by_class_name("st")
                data = {
                    "search_title": title.text,
                    "search_result": summary.text,
                    "label": q['question']
                }
                result_list.append(data)
            except:
                continue
        if len(result_list) > 0:
            collection_googleresult.insert_many(result_list)
            result_list.clear()

        collection_question.update_one(
            {'_id': q['_id']}
            , {'$set': {'isDeal': 'Y'}
               }
        )

    client.close()
    browser.quit()


if __name__ == '__main__':
    main()
