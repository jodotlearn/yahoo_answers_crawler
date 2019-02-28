# encoding: utf-8
import json
import time

from bs4 import BeautifulSoup
from jsoncomment import JsonComment
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def main():
    question_list = []
    # mongodb_uri = 'mongodb://udiclab:udiclab@127.0.0.1/yahoo_answers'
    # client = MongoClient(mongodb_uri, 10017)
    # db = client['yahoo_answers']
    # collect = db['questions']

    with open('source/categories.json', 'r', encoding='utf-8') as f:
        parser = JsonComment(json)
        categories = parser.load(f)


    searchbox_id = "UHSearchBox"
    searchbutton_id = "UHSearchProperty"
    chrome_driver = '/Users/jo/Documents/workspaces/python/yahoo_answers_crawler/driver/chromedriver'
    browser = webdriver.Chrome(chrome_driver)
    base_url = "https://tw.answers.yahoo.com/"

    for item in categories:
        arr = item.split("|")
        if len(arr) == 2:
            words = arr[0] + ' ' + arr[1]
        elif len(arr) == 3:
            # words = arr[0] + ' ' + arr[1] + ' ' + arr[2] # less query result
            words = arr[0] + ' ' + arr[2] # more query result
        else:
            continue

        browser.get(base_url)
        searchbox = browser.find_element_by_id(searchbox_id)
        searchbox.clear()
        searchbox.send_keys(words)
        browser.find_element_by_id(searchbutton_id).click()
        pageCount = 0
        while True:
            time.sleep(3)
            pageCount += 1
            if pageCount>100:
                break

            html_source = browser.page_source
            soup = BeautifulSoup(html_source, "html.parser")
            # get all articles
            try:
                results = soup.find('div', {'id': 'web'}) \
                    .find('ol', {'class': ' reg searchCenterMiddle'}) \
                    .findAll('div', {'class': 'compTitle'})

                for r in results:
                    question_dict = {
                        "category": item,
                        "question": r.text,
                        "isValid": ""
                    }
                    # rec_id = collect.insert_one(question_dict).inserted_id
                    # question_dict.update({'_id':str(rec_id)})
                    question_list.append(question_dict)

                # find the next link, break the loop if not found
                try:
                    next = browser.find_element_by_css_selector("a.next")
                    next.click()
                except NoSuchElementException:
                    break
            except:
                break
        # if len(question_list) > 0:
        #     collect.insert_many(question_list)
        #     question_list.clear()

    # results = {
    #     "datas":question_list
    # }
    with open('output/questions.json', 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, ensure_ascii=False, indent=4)

    browser.quit()


if __name__ == '__main__':
    main()
