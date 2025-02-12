from os import getenv
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
POST_URL = getenv('POST_URL')
LOGIN_URL = getenv('LOGIN_URL')
session = requests.Session()
def set_auth_token():
    auth_response = session.post(LOGIN_URL, data={"username": 'test@gmail.com', "password": 'test'})
    if auth_response.status_code != 200:
        raise ValueError("Failed to authenticate")
    token = session.cookies.get_dict()['recipe_user']
    session.cookies.set("recipe_user", f"{token}")


def write_to_db_by_FastAPI(name, description, ingredients, steps):
    data = {'name': name, 'description': description, 'ingredients': ingredients, 'steps': steps}
    fastapi_response = session.post(POST_URL, json=data)
    if fastapi_response.status_code == 200:
        print(fastapi_response.json())
    else:
        print(fastapi_response.status_code)


def clean_time_to_minuets(soup):
    dirty_time = soup.select_one('#pt_steps strong').text
    if 'д' in dirty_time:
        clean_time = int(dirty_time.split()[0]) * 1440
    elif 'ч' in dirty_time and 'мин' in dirty_time:
        time = dirty_time.split()
        hours = int(time[0]) * 60
        minutes = int(time[2])
        clean_time = hours + minutes
    elif 'ч' in dirty_time:
        clean_time = int(dirty_time.split()[0]) * 60
    elif 'мин' in dirty_time:
        clean_time = int(dirty_time.split()[0])
    else:
        clean_time = 10
    return clean_time


def parse_recipes():
    set_auth_token()
    for i in range(1, 3):
        url = f'https://1000.menu/ajax/free/content_ratings/all?page={i}'
        response = requests.get(url=url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        recipes_links = ['https://1000.menu' + link['href'] for link in soup.find_all('a', class_='h5')]
        for link in recipes_links:
            response = requests.get(url=link)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            name = soup.select_one('h1').text
            description = soup.select_one('.description').text
            ingredients = [{"name": i['content'].split('-')[0].strip(), "quantity": i['content'].split('-')[-1].strip()}
                           for i in soup.select('#ingredients #recept-list .ingredient [itemprop="recipeIngredient"]')]
            steps_values = soup.select('.instructions li p')
            time = int(clean_time_to_minuets(soup) / len(steps_values))
            steps = [{'step_description': i.text.strip(), 'step_time': time} for i in steps_values]
            write_to_db_by_FastAPI(name, description, ingredients, steps)


if __name__ == "__main__":
    print('Сейчас начнётся парсинг данных и заполнение бд. Вы можете дальше пользовать API в процессе заполнения')
    parse_recipes()
