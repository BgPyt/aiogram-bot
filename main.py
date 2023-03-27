import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from request import HH
from models import User
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

TOKEN = '6063313725:AAGot8z_dk-onbzQciuVv9a-PZt4FtNgXtk'
bot = Bot(token=TOKEN)
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
        return await msg.answer(f'Я бот. Приятно познакомиться, {msg.from_user.first_name}')
    return await msg.answer(f'Давно вас не было, {msg.from_user.first_name}')


class VacancySearch(StatesGroup):
    name = State()


@dp.message_handler(commands=['search'])
async def search(msg: types.Message):
    await msg.reply('Какие вакансии будем искать?')
    await VacancySearch.name.set()


@dp.message_handler(state=VacancySearch.name)
async def process_name(msg: types.Message, state: FSMContext):
    a1 = dp._loop_create_task(HH.get_links(msg.text.lower()))
    for a in await asyncio.get_event_loop().run_until_complete(a1):
        await msg.answer(asyncio.get_event_loop().run_until_complete(HH.get_resume(a)))










if __name__ == '__main__':
   executor.start_polling(dp)
