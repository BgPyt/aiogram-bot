import requests
from bs4 import BeautifulSoup
import fake_useragent
import json
import time
import re
import asyncio
import datetime

UA = fake_useragent.UserAgent()


def get_links(name, income, experience, schedule):
    data = requests.get(
        url=f'https://kemerovo.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={name}&order_by=publication_time{income}{experience}{schedule}',
        headers={"user-agent": UA.random})
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        page_count = int(
            soup.find('div', attrs={'class': "pager"}).find_all("span", recursive=False)[-1].find("a").find(
                "span").text)
    except:
        for a in soup.find_all("a", attrs={"class": "serp-item__title"}):
            yield f"{a.attrs['href'].split('?')[0]}"
    else:
        for page in range(page_count):
            try:
                data = requests.get(
                    url=f'https://kemerovo.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={name}&order_by=publication_time&page={page}{income}{experience}{schedule}',
                    headers={"user-agent": UA.random})
                if data.status_code != 200:
                    continue
                soup = BeautifulSoup(data.content, 'lxml')
                for a in soup.find_all("a", attrs={"class": "serp-item__title"}):
                    yield f"{a.attrs['href'].split('?')[0]}"
            except Exception as e:
                print(f"{e}")
            time.sleep(1)


def get_resume(link, new_date=None):
    mouth = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5,
             'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9, 'октярбря': 10,
             'ноября': 11, 'декабря': 12}
    try:
        data = requests.get(
            url=link,
            headers={"user-agent": UA.random}
        )
        if data.status_code != 200:
            return
        soup = BeautifulSoup(data.content, 'lxml')
        date = soup.find('p', attrs={"class": "vacancy-creation-time-redesigned"}).text
        if new_date:
            specific = date.split()[2:5]
            if datetime.date(int(specific[2]), int(mouth[specific[1]]), int(specific[0])) != new_date:
                return None
        name_vacancy = soup.find('h1',
                                 attrs={"class": "bloko-header-section-1", 'data-qa': "vacancy-title"}).text
        experience = soup.find('span', attrs={"data-qa": "vacancy-experience"}).text
        salary = soup.find('div', attrs={"data-qa": "vacancy-salary"}).text
        chart = soup.find('p', attrs={"data-qa": "vacancy-view-employment-mode"}).text
        description = soup.find('div', attrs={"data-qa": 'vacancy-description'}).text
        new_line = "\n"
        description = "".join([(word + new_line) if re.search("[:;.]", word) else f'{word} ' for word in description.split()])
        return f'Название вакансии: {name_vacancy}\nЗарплата: {salary}\nОпыт: {experience}\nОписание:\n {description}\nТип занятости и график: {chart}\n' \
               f'Дата и город: {" ".join(date.split()[2:])}\n' \
               f'Ccылка на вакансию: {link}\n_____'

    except Exception as e:
        return None

def form(text, category):
    '''Преобразование выбранной фильтра в параметр url '''
    if category is None:
        return ''.join([i for i in text.string if i.isdigit()])
    elif category == 'experience':
        other = ''.join([i for i in text if i.isdigit()])
        if other == '13':
            return 'between1And3'
        elif other == '36':
            return 'between3And6'
        elif other == '6':
            return 'moreThan6'
        else:
            return 'noExperience'
    elif category == 'work_schedule':
        if text == 'Полный день':
            return 'fullDay'
        elif text == 'Вахтовый метод':
            return 'flyInFlyOut'
        elif text == 'Сменный график':
            return 'shift'
        elif text == 'Удаленная работа':
            return 'remote'
        else:
            return 'flexible'






def filter_vacancy(name, index=2, income='', experience='', interval=-1, filter='&salary=', category=None, select='bloko-radio__text'):
    if income == 'Не имеет значения':
        income = ''
    if experience == 'Не имеет значения':
        experience = ''
    data = requests.get(
        url=f'https://kemerovo.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={name}&order_by=publication_time{income}{experience}',
        headers={"user-agent": UA.random})
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    html = soup.find_all("fieldset", attrs={"class": "novafilters-group-wrapper"})[index].find_all("span", attrs={
        "class": f"{select}"})
    dict_value = {}
    if interval:
        html = html[1:]
    if interval == -1:
        html = html[:-1]
    for i in html:
        try:
            text = i.find("span").string
            count_vac = re.sub(r'\u202f', '',
                               str(i.find("span", attrs={"class": "bloko-text bloko-text_tertiary"}).string))
            dict_value[f'{text}(нашлось:{count_vac})'] = filter + form(text, category)
        except:
            continue
    dict_value['Не имеет значения'] = ''
    if not dict_value:
        return None
    return dict_value




