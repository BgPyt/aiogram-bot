import requests
from bs4 import BeautifulSoup
import fake_useragent
import json
import time
import re
import asyncio


UA = fake_useragent.UserAgent()
class HH:

    async def get_links(text):
        data = requests.get(
            url=f'https://kemerovo.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&order_by=publication_time&page=1',
            headers={"user-agent": UA.random})
        if data.status_code != 200:
             return
        soup = BeautifulSoup(data.content, 'lxml')
        try:
            page_count = int(
                soup.find('div', attrs={'class': "pager"}).find_all("span", recursive=False)[-1].find("a").find(
                    "span").text)
        except:
             return
        for page in range(page_count):
            try:
                data = requests.get(
                    url=f'https://kemerovo.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&page={page}',
                    headers={"user-agent": UA.random})
                if data.status_code != 200:
                    continue
                soup = BeautifulSoup(data.content, 'lxml')
                for a in soup.find_all("a", attrs={"class": "serp-item__title"}):
                    yield f"{a.attrs['href'].split('?')[0]}"
            except Exception as e:
                print(f"{e}")
            await asyncio.sleep(1)

    async def get_resume(link):
        try:
            data = requests.get(
                url=link,
                headers={"user-agent": UA.random}
            )
            if data.status_code != 200:
                return
            soup = BeautifulSoup(data.content, 'lxml')
            date = soup.find('p', attrs={"class": "vacancy-creation-time-redesigned"}).text
            name_vacancy = soup.find('h1',
                                     attrs={"class": "bloko-header-section-1", 'data-qa': "vacancy-title"}).text
            experience = soup.find('span', attrs={"data-qa": "vacancy-experience"}).text
            salary = soup.find('div', attrs={"data-qa": "vacancy-salary"}).text
            chart = soup.find('p', attrs={"data-qa": "vacancy-view-employment-mode"}).text
            description = soup.find('div', attrs={"data-qa": 'vacancy-description'}).text
            new_line = "\n"
            return await f'Название вакансии: {name_vacancy}\nЗарплата: {salary}\nОпыт: {experience}\nОписание:\n {" ".join([(word + new_line) if re.search("[:;.]", word) else word for word in description.split()])}\nТип занятости и график: {chart}\n' \
                         f'Дата и город: {" ".join(date.split()[2:])}\n' \
                         f'Ccылка на вакансию: {a}\n_____'

            await asyncio.sleep(1)
        except Exception as e:
            return await f'{e}'

# if __name__ == '__main__' :
#     for a in get_links('python'):
#         print(get_resume(a))

