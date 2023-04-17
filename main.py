import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import filters
from request import *
from models import User, Filter_Vacancy
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime
import os
from dotenv import load_dotenv

load_dotenv()


bot = Bot(token=os.environ['TOKEN'])
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def start(msg: types.Message):
    if not User.filter(user_id=msg.from_user.id):
        User(user_id=msg.from_user.id,
             first_name=msg.from_user.first_name,
             username=msg.from_user.username,
             date=msg.date,
             is_bot=msg.from_user.is_bot,
             language_code=msg.from_user.language_code).save()
        return await msg.answer(f'Я бот по поиску работы на "HH.ru". Приятно познакомиться, {msg.from_user.first_name}')
    return await msg.answer(f'Давно вас не было, {msg.from_user.first_name}')


class VacancySearch(StatesGroup):
    name = State()
    income = State()
    experience = State()
    work_schedule = State()
    exit = State()

class Exit_search(StatesGroup):
    exit_search = State()
    exit_search_auto = State()



@dp.message_handler(commands=['setting'])
async def search(msg: types.Message):
    await msg.reply('Напишите ключевое слово - \n'
                    '*В названии вакансии;\n'
                    '*В названии компании;\n'
                    '*В описании вакансии;')
    await VacancySearch.name.set()


@dp.message_handler(state=VacancySearch.name)
async def process_name(msg: types.Message, state: FSMContext):
    if not msg.text:
        await msg.reply('Пустое поле недопустимо')
    try:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        vidg = filter_vacancy(msg.text)
        if not vidg:
            return await msg.answer('Увы.. не удалось найти. Попробуйте снова')
        for name in vidg:
            keyboard.add(name)
        keyboard.add('Выйти')
        await state.update_data(name=(msg.text.lower(), vidg))
        await msg.answer('Укажите уровень дохода ↓', reply_markup=keyboard)
        await VacancySearch.income.set()
    except:
        await msg.reply('Выберите из предложенных')



@dp.message_handler(state=VacancySearch.income)
async def process_income(msg: types.Message, state: FSMContext):
    '''Уровень дохода'''
    if msg.text == 'Выйти':
        await msg.reply('Успешно вышли!', reply_markup=types.ReplyKeyboardRemove())
        return await state.finish()
    try:
        filter = await state.get_data('name')
        await state.update_data(name=filter['name'][0])
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        name = await state.get_data('name')
        vidg = filter_vacancy(name=name['name'],
                              index=7,
                              income=filter['name'][1][msg.text] + '&only_with_salary=true',
                              interval=1,
                              filter='&experience=',
                              category='experience'
                              )
        if not vidg:
            return await msg.answer('Увы.. не удалось найти. Попробуйте снова')
        for name in vidg:
            keyboard.add(name)
        keyboard.add('Выйти')
        await msg.answer('Укажите опыт работы ↓', reply_markup=keyboard)
        await state.update_data(income=(filter['name'][1][msg.text] + '&only_with_salary=true', vidg))
        await VacancySearch.experience.set()
    except:
        await msg.reply('Выберите из предложенных')


@dp.message_handler(state=VacancySearch.experience)
async def process_experience(msg: types.Message, state: FSMContext):
    '''Опыт работы'''
    if msg.text == 'Выйти':
        await msg.reply('Успешно вышли!', reply_markup=types.ReplyKeyboardRemove())
        return await state.finish()
    try:
        filter = await state.get_data('income')
        await state.update_data(income=filter['income'][0])
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        name = await state.get_data('name')
        income = await state.get_data('income')
        vidg = filter_vacancy(name=name['name'],
                              index=9,
                              income=income['income'],
                              experience=filter['income'][1][msg.text],
                              interval=None,
                              filter='&schedule=',
                              category='work_schedule',
                              select='bloko-checkbox__text'
                              )
        if not vidg:
            return await msg.answer('Увы.. не удалось найти. Попробуйте снова')
        for name in vidg:
            keyboard.add(name)
        keyboard.add('Выйти')
        await state.update_data(experience=(filter['income'][1][msg.text], vidg))
        await msg.answer('Укажите график работы ↓', reply_markup=keyboard)
        await VacancySearch.work_schedule.set()
    except:
        await msg.reply('Выберите из предложенных')


@dp.message_handler(state=VacancySearch.work_schedule)
async def process_schedule(msg: types.Message, state: FSMContext):
    '''График работы'''
    if msg.text == 'Выйти':
        await msg.reply('Успешно вышли!', reply_markup=types.ReplyKeyboardRemove())
        return await state.finish()
    try:
        filter = await state.get_data()
        await state.update_data(work_schedule=filter['experience'][1][msg.text])
        await state.update_data(experience=filter['experience'][0])
        filter = await state.get_data()
        await state.finish()
        try:
            old_flt = Filter_Vacancy.get(user=User.get(user_id=msg.from_user.id).id)
            if old_flt:
                old_flt.delete_instance()
        except:
            pass
        finally:
            Filter_Vacancy(name=filter['name'],
                           income=filter['income'],
                           schedule=filter['work_schedule'],
                           experience=filter['experience'],
                           user=User.get(user_id=msg.from_user.id).id).save()
            return await msg.reply('Настройки успешно сохранены!', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        await msg.reply('Выберите из предложенных')


@dp.message_handler(commands=['search_auto'])
async def process_search_auto(msg: types.Message, state: FSMContext):
    try:
        user = Filter_Vacancy.get(user=User.get(user_id=msg.from_user.id).id)
        name = user.name
        income = user.income
        schedule = user.schedule
        experience = user.experience
        start_date = datetime.date.today()
        await msg.reply('Я буду вас уведомлять с завтрашнего дня новыми вакансиями каждый день\n'
                        'Пока вы мне не скажите слово: "Остановить"')
        await state.update_data(exit_search_auto=True)
        while True:
            await asyncio.sleep(3600)
            if not (await state.get_data())['exit_search_auto']:
                break
            new_date = datetime.date.today()
            if start_date != new_date:
                if not (await state.get_data())['exit_search_auto']:
                    break
                for i in get_links(name, income, experience, schedule):
                    if not (await state.get_data())['exit_search_auto']:
                        break
                    answer = get_resume(i, new_date)
                    if answer:
                        await msg.answer(answer)
                        await asyncio.sleep(5)


    except:
        await msg.reply('Установите настройки фильтрации для автоматического поиска')

@dp.message_handler(commands=['show_setting'])
async def show_setting(msg: types.Message):
    try:
        user = Filter_Vacancy.get(user=User.get(user_id=msg.from_user.id).id)
        sched = {'&schedule=fullDay': 'Полный день', '&schedule=remote': 'Удаленная работа',
               '&schedule=flexible': 'Гибкий график', '&schedule=shift': 'Сменный график',
               '&schedule=flyInFlyOut': 'Вахтовый метод'}
        exp = {'&experience=between1And3': 'От 1 года до 3 лет',
               '&experience=between3And6': 'От 3 до 6 лет',
               '&experience=moreThan6': 'Более 6 лет',
               '&experience=noExperience': 'Нет опыта'}
        salary = "".join([i for i in user.income if i.isdigit()])
        return await msg.reply(f'Ключевое слово: {user.name}\n' 
                               f'Уровень дохода: {"{:,}".format(int(salary)) if user.income else "Пустое поле"}\n'
                               f'Опыт работы: {exp[user.experience] if user.experience else "Пустое поле"}\n'
                               f'График работы: {sched[user.schedule] if user.schedule else "Пустое поле"}')

    except Exception as e:
        print(e)
        await msg.reply('Отсутсвуют настройки фильтрации')


@dp.message_handler(commands=['search'])
async def process_search(msg: types.Message, state: FSMContext):
    try:
        user = Filter_Vacancy.get(user=User.get(user_id=msg.from_user.id).id)
        name = user.name
        income = user.income
        schedule = user.schedule
        experience = user.experience
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Выход')
        await msg.reply('Начался поиск...', reply_markup=keyboard)
        await state.update_data(exit_search=True)
        for i in get_links(name, income, experience, schedule):
            bool = await state.get_data()
            if not bool['exit_search']:
                await msg.answer('Поиск завершен', reply_markup=ReplyKeyboardRemove())
                break
            await msg.answer(get_resume(i))
            await asyncio.sleep(5)


    except Exception as e:
        await msg.reply('Установите настройки фильтрации для поиска')
        print(e)


@dp.message_handler(filters.Text(equals=['Выход', 'Остановить'], ignore_case=True))
async def exit_system_search(msg: types.Message, state: FSMContext):
    try:
        bool_search = await state.get_data()
        try:
            if bool_search['exit_search'] and msg.text == 'Выход':
                return await state.update_data(exit_search=False)
        except:
            if bool_search['exit_search_auto'] and msg.text == 'Остановить':
                await state.update_data(exit_search_auto=False)
                return await msg.answer('Автоматический поиск остановлен.')
    except:
        pass


if __name__ == '__main__':
    os.system('python models.py')
    executor.start_polling(dp)
