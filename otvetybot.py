import re
import urllib.parse

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, MediaGroupFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils import executor
from aiogram.utils.markdown import hide_link
import datetime
from aiogram.utils.deep_linking import decode_payload
from aiogram_media_group import media_group_handler
from typing import List
from botdb import DBclass, Post

# logging.basicConfig(level=logging.INFO)
db = DBclass('dbbot.db')
bot = Bot(token="6030592765:AAF6iCf__gOiVohE4cujp7loBuMHqU8aCL4")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# -------------------------
# ID OF FILE BOT
filebotid = -1001933035686
# ID OF PUBLIC CHANNEL
publicationbotid = -1001830791619
# ID'S OF CHAT BOTS
chatbotids = [-1001801606004, -1001605913621]
occupiedchats = []
# -------------------------



class NewPost(StatesGroup):
    protection = State()
    theme = State()
    maintext = State()
    price = State()
    filehandle = State()
    publish = State()

class MyPosts(StatesGroup):
    choice = State()
    deleteorback = State()

class TakePosts(StatesGroup):
    approving = State()
class MyMoney(StatesGroup):
    vibor = State()
    deleteorback = State()

# USER SIDE ----------------------------------------------------
# start handler - give menu
@dp.message_handler(commands=['start', 'menu'], state='*')
async def command_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    payload = decode_payload(args)
    # I take post 1
    if payload:
        post = db.findpost(payload)[0]
        if message.from_user.id == post[1]:
            await bot.send_message(message.chat.id, 'Вы кликнули на свой же пост!')
            # ------------------------

            await message.answer(f"Вы отправили заявку чтобы выполнить задание. Автор рассмотрит эту заявку и сможет ее принять, после чего вы будете направлены в личный чат {hide_link(post[10])}", parse_mode=types.ParseMode.HTML)

            # data-----------------------------
            encoded_data = urllib.parse.urlencode({
                "completer": message.chat.id,
                "postid": post[0]
            })

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Подтвердить', callback_data=f'takeapprove{encoded_data}')
            item2 = types.InlineKeyboardButton('Отклонить', callback_data=f'takenot{encoded_data}')
            markup.add(item1, item2)

            await bot.send_message(post[1], f"Пользователь {message.from_user.full_name} готов выполнить ваше задание {hide_link(post[10])}", reply_markup=markup, parse_mode=types.ParseMode.HTML)

        else:
            await message.answer(
                f"Вы отправили заявку чтобы выполнить задание. Автор рассмотрит эту заявку и сможет ее принять, после чего вы будете направлены в личный чат {hide_link(post[10])}",
                parse_mode=types.ParseMode.HTML)

            # data-----------------------------
            encoded_data = urllib.parse.urlencode({
                "completer": message.chat.id,
                "postid": post[0]
            })

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Подтвердить', callback_data=f'takeapprove{encoded_data}')
            item2 = types.InlineKeyboardButton('Отклонить', callback_data=f'takenot{encoded_data}')
            markup.add(item1, item2)

            await bot.send_message(post[1],
                                   f"Пользователь {message.from_user.full_name} готов выполнить ваше задание {hide_link(post[10])}",
                                   reply_markup=markup, parse_mode=types.ParseMode.HTML)

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Новый пост', 'Мои посты', 'Мои деньги')
        db.makeuser(message.chat.id, message.from_user.full_name)


        await message.answer(f'Здравствуйте, это бот паблика «TurtleUA», выберите одно действие из меню.', reply_markup=markup)
#start2
@dp.message_handler(lambda message: message.text in ['Новый пост', 'Мои посты', 'Мои деньги'], state='*')
async def starthandlertwo(message: types.Message, state: FSMContext):
    # New Post 1
    if message.text == 'Новый пост':

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton('Защищенный', callback_data='protected')
        item2 = types.InlineKeyboardButton('Обычный', callback_data='ordinary')
        markup.add(item1, item2)
        msg = await bot.send_message(message.chat.id, "Загрузка...", reply_markup=types.ReplyKeyboardRemove())
        await msg.delete()
        await bot.send_message(message.chat.id, 'Защищеный или обычный пост: ', reply_markup=markup)
        await NewPost.protection.set()
# ______________________________________

    # My Posts 1
    elif message.text == 'Мои посты':
        if db.findallposts(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            posts = db.findallposts(message.chat.id)
            n = 0
            for i in posts:
                p = types.InlineKeyboardButton(f'{i[5]}, {i[6]}, {i[2]}',
                                                   callback_data=f'myposts{str(n)}')
                markup.add(p)
                n += 1
            await MyPosts.choice.set()
            await bot.send_message(message.chat.id, 'Выберите одну публикацию', reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "У вас нету публикаций")


# --------------------------------------
# New Post 2
@dp.callback_query_handler(lambda call: call.data in ['protected', 'ordinary'], state=NewPost.protection)
async def newpostprotection(callbackQuery: types.CallbackQuery, state: FSMContext):
    if callbackQuery.data == 'protected':
        # DATA
        async with state.proxy() as data:
            data["protection"] = callbackQuery.data

        await bot.edit_message_text('Укажите название предмета или тему задания', callbackQuery.message.chat.id, callbackQuery.message.message_id)
        await NewPost.next()
    elif callbackQuery.data == 'ordinary':
        # DATA
        async with state.proxy() as data:
            data["protection"] = callbackQuery.data
        await bot.edit_message_text('Укажите название предмета или тему задания', callbackQuery.message.chat.id, callbackQuery.message.message_id)
        await NewPost.next()

# New Post 3
@dp.message_handler(state=NewPost.theme)
async def newposttheme(message: types.Message, state: FSMContext):
    # DATA
    async with state.proxy() as data:
        data["theme"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Отменить')

    await bot.send_message(message.chat.id, f"Напишите краткое описание того, что нужно сделать", reply_markup=markup)
    await NewPost.next()

# New Post 4
@dp.message_handler(state=NewPost.maintext)
async def newposttext(message: types.Message, state: FSMContext):
    #cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Новый пост', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.chat.id, "Отменено", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Договорная', 'Отменить')
        # DATA
        async with state.proxy() as data:
            data["maintext"] = message.text

        await bot.send_message(message.chat.id, f"Назвите цену или нажмите «Договорная» \n\nНапример, чтобы указать цену в 100 грн, введите «100»", reply_markup=markup)
        await NewPost.next()

# New Post 5
@dp.message_handler(state=NewPost.price)
async def newpostprice(message: types.Message, state: FSMContext):
    # cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Новый пост', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.chat.id, "Отменено", reply_markup=markup)
    else:
        if message.text == "Договорная":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Готово', 'Отменить')
            # DATA
            async with state.proxy() as data:
                data["price"] = message.text
                data["mediaid"] = []
                data["docid"] = []
            await bot.send_message(message.chat.id, f"Теперь добавьте файл или фото, ассоциированый с заданием, затем нажмите «Готово»", reply_markup=markup)
            await NewPost.next()

        elif message.text.isnumeric():

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Готово', 'Отменить')

            # DATA
            async with state.proxy() as data:
                data["price"] = message.text
                data["mediaid"] = []
                data["docid"] = []
            await bot.send_message(message.chat.id, f"Теперь добавьте файл или фото, ассоциированый с заданием, затем нажмите «Готово»", reply_markup=markup)
            await NewPost.next()

        else:
            await bot.send_message(message.chat.id, f"Ошибка в указании цены, правильно указать цену без текста\nНапример, чтобы указать цену в 100 грн, введите «100»")



# New post 6 one doc one photo
@dp.message_handler(MediaGroupFilter(is_media_group=False), content_types=['photo', 'document'], state=NewPost.filehandle)
async def fileHandle(message: types.Message, state: FSMContext):

    if message.photo:
        # Handle photo
        photo = message.photo[-1]
        file_id = photo.file_id


        # DATA
        async with state.proxy() as data:
            data["mediaid"].append(file_id)


    elif message.document:
        # Handle document
        document = message.document
        file_id = document.file_id

        # DATA
        async with state.proxy() as data:
            data["docid"].append(file_id)


# New post 6
@dp.message_handler(MediaGroupFilter(is_media_group=True), content_types=['photo', 'document'], state=NewPost.filehandle)
@media_group_handler
async def album_handler(messages: List[types.Message], state: FSMContext):
    for message in messages:

        if message.photo:
            # Handle photo
            document = message.photo[-1]
            file_id = document.file_id
            async with state.proxy() as data:
                data["mediaid"].append(file_id)
        elif message.document:
            # Handle document
            document = message.document
            file_id = document.file_id
            async with state.proxy() as data:
                data["docid"].append(file_id)

# New post 7 If user chooses, he could edit the post
@dp.message_handler(state=NewPost.filehandle)
async def newpostfilegotovo(message: types.Message, state: FSMContext):
    # cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Новый пост', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.chat.id, "Отменено", reply_markup=markup)
    else:
        if message.text == "Готово":
            media = types.MediaGroup()
            docs = []



            async with state.proxy() as data:
                data["doclink"] = []
                for i in data["mediaid"]:
                    media.attach_photo(photo=i)
                for j in data["docid"]:
                    filemessagedoc = await bot.send_document(filebotid, j)
                    docs.append(hide_link(filemessagedoc.url))
                    data["doclink"].append(hide_link(filemessagedoc.url))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Опубликовать', 'Отменить')

            async with state.proxy() as data:
                data["medialink"] = ""

                #media
                if len(data["mediaid"])>0:
                    filemessagephoto = await bot.send_media_group(filebotid, media)
                    data["medialink"] = hide_link(filemessagephoto[0].url)
                #post
                post = Post(active="Активный", author=message.from_user.id, completer="Нету",
                            theme=data["theme"], maintext=data["maintext"], price=data["price"], mediaid=data["medialink"], docid=data["doclink"], protection=data["protection"])
                data["post"] = post
            #message

            #send
            await bot.send_message(message.chat.id, "Отлично, пост готов. Если вы хотите изменить что-либо, просто измените сообщения которые вы отправили ранее. Затем, нажмите Опубликовать", reply_markup=markup)
            await bot.send_message(message.chat.id, post.tostring(), parse_mode=types.ParseMode.HTML)
            await NewPost.next()

# New post 8 Final, publish to main channel
@dp.message_handler(state=NewPost.publish)
async def newpostpublish(message: types.Message, state: FSMContext):
    # cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Новый пост', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.chat.id, "Отменено", reply_markup=markup)
    else:
        if message.text == 'Опубликовать':
            markup = types.InlineKeyboardMarkup()
            # chat1

            async with state.proxy() as data:
                postid = db.publishpost(data["post"])

                link = await get_start_link(str(postid), encode=True)

                item1 = types.InlineKeyboardButton('Беру', url=link)
                markup.add(item1)

                publishedmessage = await bot.send_message(publicationbotid, data["post"].tostring(), reply_markup=markup, parse_mode=types.ParseMode.HTML)
                #linkhandle
                linktopublished = publishedmessage.url
                db.givepostalink(postid, linktopublished)


            #user

            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup2.add('Новый пост', 'Мои посты', 'Мои деньги')
            await bot.send_message(message.chat.id, f"Пост опубликован на основном канале {hide_link(linktopublished)}", reply_markup=markup2, parse_mode=types.ParseMode.HTML)
            await state.finish()

# My posts2
@dp.callback_query_handler(lambda call: call.data in [f'myposts{str(x)}' for x in range(len(db.findallposts(call.message.chat.id)))], state=MyPosts.choice)
async def mypostsshow(call: types.CallbackQuery, state: FSMContext):
    ind = str(call.data).replace('myposts', '')
    post = db.findallposts(call.message.chat.id)[int(ind)]
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Удалить', callback_data='postdelete')
    item2 = types.InlineKeyboardButton('Назад', callback_data='postback')
    markup.add(item1, item2)

    async with state.proxy() as data:
        data["post"] = post

    await bot.edit_message_text(f"<b>Статус:</b> {post[2]}\n<b>Выполнитель:</b> {post[3]}\n<b>Тип поста:</b> {'Защищённый пост' if post[4]=='protected' else 'Обычный пост'}\n<b>Тема:</b> {post[5]}\n<b>Задание:</b> {post[6]}\n<b>Цена:</b> {post[7]}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.HTML)
    await MyPosts.next()

# My posts 3
@dp.callback_query_handler(lambda call: call.data in ['postdelete', 'postback'], state=MyPosts.deleteorback)
async def mypostsdelete(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'postdelete':
        async with state.proxy() as data:
            db.deletepost(data["post"][0])
            message_id = re.search(r'/(\d+)$', data["post"][10]).group(1)
            await bot.delete_message(publicationbotid, message_id)

        await bot.edit_message_text("Пост удалён!", call.message.chat.id, call.message.message_id)

    elif call.data == 'postback':
        if db.findallposts(call.message.chat.id):
            markup = types.InlineKeyboardMarkup()
            posts = db.findallposts(call.message.chat.id)
            n = 0
            for i in posts:
                p = types.InlineKeyboardButton(f'{i[5]},  {i[6]}, {i[2]}',
                                                   callback_data=f'myposts{str(n)}')
                markup.add(p)
                n += 1
            await MyPosts.choice.set()
            await bot.edit_message_text('Выберите одну публикацию', call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            await bot.send_message(call.message.chat.id, "У вас нету публикаций")
# I take post 2
@dp.callback_query_handler(lambda call: call.data.startswith('takeapprove') or call.data.startswith('takenot'), state='*')
async def approvingproc(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('takeapprove'):
        #get link for chat
        markup = types.InlineKeyboardMarkup()
        freechat = chatbotids.pop()
        occupiedchats.append(freechat)



        #data
        encodeddata = call.data[11:]
        decoded_data = urllib.parse.parse_qs(encodeddata)

        completer = decoded_data["completer"][0]
        postid = decoded_data["postid"][0]

        post = db.findpost(postid)[0]
        postlink = post[10]
        #datafinish

        # write data to chat db

        invitelink = await bot.create_chat_invite_link(freechat)

        item1 = types.InlineKeyboardButton('Открыть чат', url=f"{invitelink.invite_link}")
        markup.add(item1)
        await bot.edit_message_text('***Вы приняли заявку***\n\nТеперь вы можете открыть чат', call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
        await bot.send_message(completer, f"<b>Пользователь</b> принял вашу заявку {hide_link(postlink)}", parse_mode=types.ParseMode.HTML, reply_markup=markup)

    elif call.data.startswith('takenot'):
        #data
        encodeddata = call.data[7:]
        decoded_data = urllib.parse.parse_qs(encodeddata)

        completer = decoded_data["completer"][0]
        postid = decoded_data["postid"][0]

        post = db.findpost(postid)[0]
        postlink = post[10]

        await bot.edit_message_text('Вы отклонили заявку на выполнение работы.', call.message.chat.id, call.message.message_id)
        await bot.send_message(completer, f"Пользователь отклонил вашу заявку на выполнение работы {hide_link(postlink)}", parse_mode=types.ParseMode.HTML)

# I take post 3
@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def welcome_new_user(message: types.Message):
    if message.chat.id in occupiedchats:

        #db => kto zashel |vipolnitel|

        pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)