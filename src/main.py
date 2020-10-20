# coding: utf-8
import re
import requests
from bs4 import BeautifulSoup
from time import sleep
from src.Calender import Calender

colorId = 0


def get_retry(url, retry_times=5):
    for t in range(retry_times + 1):
        r = requests.get(url)
        if t < retry_times:
            try:
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(e)
                sleep(10)
                continue
        return r


def get_title(bs, year):
    return re.sub(
        r'\s+',
        ' ',
        bs.find('h2').text.replace(f"{year}年度", '').strip()
    )


def main():
    global colorId
    calender = Calender()

    # base
    base_url = "https://syllabus.naist.jp"
    list_url = f"{base_url}/subjects/preview_list"

    # syllabuses list
    list_response = get_retry(list_url)
    list_bs = BeautifulSoup(list_response.content, "html.parser")
    syllabuses = list_bs.select('.w20pr a')

    for syllabus in syllabuses:
        subject_name = syllabus.text
        subject_url = base_url + syllabus.get('href')
        print(subject_name, subject_url)
        subject_response = get_retry(subject_url)
        subject_bs = BeautifulSoup(subject_response.content, "html.parser")
        class_info = subject_bs.select('.tbl01.mB20')[3]

        if "表示可能なデータがありません。" in class_info.text:
            schedules = subject_bs.select('.tbl01.mB20')[5].select('tr td')
            if len(schedules) == 1:
                continue
            title = get_title(subject_bs, calender.year)
            calender.add_schedules(title, subject_url, schedules, colorId)
            sleep(1)
        else:
            for class_detail in class_info.select('.btn02.w55'):
                subject_url = base_url + class_detail.get('href')
                print(subject_url)
                subject_response = get_retry(subject_url)
                subject_bs = BeautifulSoup(
                    subject_response.content, "html.parser")
                schedules = subject_bs.select(
                    '.tbl01.mB20')[4].select('tr td')
                if len(schedules) == 1:
                    continue
                title = get_title(subject_bs, calender.year)
                calender.add_schedules(title, subject_url, schedules, colorId)
                sleep(1)
        colorId = (colorId + 1) % 11
