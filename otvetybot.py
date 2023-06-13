import asyncio
import re
import urllib.parse
from datetime import datetime, timedelta
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, MediaGroupFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils import executor
from aiogram.utils.markdown import hide_link
from aiogram.utils.deep_linking import decode_payload
from aiogram_media_group import media_group_handler
from typing import List
from botdb import DBclass, Post
from fondy import API

# logging.basicConfig(level=logging.INFO)
db = DBclass('dbbot.db')
bot = Bot(token="6030592765:AAF6iCf__gOiVohE4cujp7loBuMHqU8aCL4")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
api = API(merchant_id="1526526", merchant_key="rj6IEGhpd3tJsfMZhbCqtU8hNo5KIo8Z", server_callback_url="https://t.me/otvetynaizibot")

# -------------------------
# ID OF FILE BOT
filebotid = -1001933035686
# ID OF PUBLIC CHANNEL
publicationbotid = -1001830791619
# ID'S OF CHAT BOTS
chatbotids = [-1001605913621, -1001801606004, -1001800064192, -1001595908456, -1001843081062, -1001658458727]
# ID superuser
superuserid = 444768059
supergroupid = -1001962874240
# -------------------------------------
for i in chatbotids:
    db.createchat(i)
# -------------------------
class NewPost(StatesGroup):
    protection = State()
    theme = State()
    maintext = State()
    price = State()
    filehandle = State()
    publish = State()
class BecomeCompleter(StatesGroup):
    name = State()
    email = State()
    date = State()
    phone = State()
    ack = State()
class MyPosts(StatesGroup):
    choice = State()
    deleteorback = State()
class CancelDeal(StatesGroup):
    ackgnowledgment = State()
class TakePosts(StatesGroup):
    approving = State()
class Pozvatchela(StatesGroup):
    pozvatstate = State()
class MyMoney(StatesGroup):
    vibor = State()
    deleteorback = State()
class MyChats(StatesGroup):
    chatschoice = State()
    backodelete = State()
class ChatChangePrice(StatesGroup):
    changingprice = State()
class DealCompleting(StatesGroup):
    completea = State()
class Withdrawing(StatesGroup):
    entercard = State()
# USER SIDE ----------------------------------------------------
# start handler - give menu
@dp.message_handler(commands=['start', 'menu'], state='*')
async def command_start(message: types.Message, state: FSMContext):
    await state.finish()
    args = message.get_args()
    payload = decode_payload(args)
    # I take post 1 ------------------------------------------------------------------------------
    if payload:
        post = db.findpost(payload)[0]
        if db.getcompleter(message.from_user.id):
            if db.getcompleter(message.from_user.id)[0][6] == 'yes':
                if message.from_user.id == post[1]:
                    await bot.send_message(message.from_user.id, 'Вы кликнули на свой же пост!')
                    # ------------------------
                    if db.postidchat(post[0]):
                        if db.postidchat(post[0])[0][2] == message.chat.id:
                            await message.answer("Вы не можете отправить больше одной заявки на один пост")
                    else:
                        await message.answer(f"Вы отправили заявку чтобы выполнить задание. Автор рассмотрит эту заявку и сможет ее принять, после чего вы будете направлены в личный чат {hide_link(post[10])}", parse_mode=types.ParseMode.HTML)

                        # data-----------------------------
                        encoded_data = urllib.parse.urlencode({
                            "completer": message.from_user.id,
                            "postid": post[0]
                        })

                        markup = types.InlineKeyboardMarkup()
                        item1 = types.InlineKeyboardButton('Подтвердить', callback_data=f'takeapprove{encoded_data}')
                        item2 = types.InlineKeyboardButton('Отклонить', callback_data=f'takenot{encoded_data}')
                        markup.add(item1, item2)

                        await bot.send_message(post[1], f"Пользователь {message.from_user.full_name} готов выполнить ваше задание {hide_link(post[10])}", reply_markup=markup, parse_mode=types.ParseMode.HTML)

                else:
                    if db.postidchat(post[0]) and db.postidchat(post[0])[0][2] == message.chat.id:
                        await message.answer("Вы не можете отправить больше одной заявки на один пост")
                    else:
                        await message.answer(
                            f"Вы отправили заявку чтобы выполнить задание. Автор рассмотрит эту заявку и сможет ее принять, после чего вы будете направлены в личный чат {hide_link(post[10])}",
                            parse_mode=types.ParseMode.HTML)

                        # data-----------------------------
                        encoded_data = urllib.parse.urlencode({
                            "completer": message.from_user.id,
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
                await message.answer("Вы не можете брать посты, потому что администратор не рассмотрел вашей заявки или отклонил её")
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add('Новый пост')
            markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
            await message.answer("Чтобы брать посты, сначала нужно стать выполнителем\n\nНажмите «Стать выполнителем» для того чтобы оставить заявку", reply_markup=markup)

    else:

        if message.chat.type == 'private':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add('Новый пост')
            markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
            db.makeuser(message.from_user.id, message.from_user.full_name)


            await message.answer(f'Здравствуйте, это бот паблика «TurtleUA», выберите одно действие из меню.', reply_markup=markup)
        elif message.chat.id in [int(item[0]) for item in db.getallchats()]:
            # if user already payed, another menu pops up
            chat = db.getchatdetails(message.chat.id)[0]
            post = db.findpost(chat[4])[0]
            lastpay = db.payidbypost(post[0])

            if lastpay:
                encoded_data = urllib.parse.urlencode({
                    "user": message.from_user.id,
                    "chatid": message.chat.id,
                })

                payment = db.getpaymentbyid(lastpay[0][0])[0]
                print(payment)
                if payment[2] == 'approved':
                    m2 = types.ReplyKeyboardRemove()
                    delmes = await bot.send_message(message.chat.id, "Загрузка...", reply_markup=m2)
                    await bot.delete_message(message.chat.id, delmes.message_id)

                    # chatmenu1

                    markup = types.InlineKeyboardMarkup(row_width=1)
                    item1 = types.InlineKeyboardButton("Поменять цену", callback_data=f"changeprice{encoded_data}")
                    item2 = types.InlineKeyboardButton("Завершить сделку", callback_data=f"dealcomplete{encoded_data}")
                    item3 = types.InlineKeyboardButton("Позвать администратора",
                                                       callback_data=f"calladminchat{encoded_data}")
                    item4 = types.InlineKeyboardButton("Отменить сделку", callback_data=f"chatdealrefuse{encoded_data}")

                    markup.add(item1, item2, item3, item4)

                    await bot.send_message(message.chat.id, "Нажмите на кнопку из меню", reply_markup=markup)
                else:

                    m2 = types.ReplyKeyboardRemove()
                    delmes = await bot.send_message(message.chat.id, "Загрузка...", reply_markup=m2)
                    await bot.delete_message(message.chat.id, delmes.message_id)

                    # chatmenu1

                    markup = types.InlineKeyboardMarkup(row_width=1)
                    item1 = types.InlineKeyboardButton("Поменять цену", callback_data=f"changeprice{encoded_data}")
                    item2 = types.InlineKeyboardButton("Оплатить", callback_data=f"payprice{encoded_data}")
                    item3 = types.InlineKeyboardButton("Позвать администратора",
                                                       callback_data=f"calladminchat{encoded_data}")
                    item4 = types.InlineKeyboardButton("Отменить сделку", callback_data=f"chatdealrefuse{encoded_data}")

                    markup.add(item1, item2, item3, item4)

                    await bot.send_message(message.chat.id, "Нажмите на кнопку из меню", reply_markup=markup)
            else:
                encoded_data = urllib.parse.urlencode({
                    "user": message.from_user.id,
                    "chatid": message.chat.id,
                })
                #removemarkp
                m2 = types.ReplyKeyboardRemove()
                delmes = await bot.send_message(message.chat.id, "Загрузка...", reply_markup=m2)
                await bot.delete_message(message.chat.id, delmes.message_id)



                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton("Поменять цену", callback_data=f"changeprice{encoded_data}")
                item2 = types.InlineKeyboardButton("Оплатить", callback_data=f"payprice{encoded_data}")
                item3 = types.InlineKeyboardButton("Позвать администратора", callback_data=f"calladminchat{encoded_data}")
                item4 = types.InlineKeyboardButton("Отменить сделку", callback_data=f"chatdealrefuse{encoded_data}")

                markup.add(item1, item2, item3, item4)

                await bot.send_message(message.chat.id, "Нажмите на кнопку из меню", reply_markup=markup)
#start2
@dp.message_handler(lambda message: message.text in ['Новый пост', 'Мои посты', 'Мои деньги', 'Мои чаты', 'Стать выполнителем'], state='*')
async def starthandlertwo(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        # New Post 1
        if message.text == 'Новый пост':

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Защищенный', callback_data='protected')
            item2 = types.InlineKeyboardButton('Обычный', callback_data='ordinary')
            markup.add(item1, item2)
            msg = await bot.send_message(message.from_user.id, "Загрузка...", reply_markup=types.ReplyKeyboardRemove())
            await msg.delete()
            await bot.send_message(message.from_user.id, 'Защищеный или обычный пост: ', reply_markup=markup)
            await NewPost.protection.set()
    # ______________________________________

        # My Posts 1
        elif message.text == 'Мои посты':
            if db.findallposts(message.from_user.id):
                markup = types.InlineKeyboardMarkup()
                posts = db.findallposts(message.from_user.id)
                n = 0
                for i in posts:
                    p = types.InlineKeyboardButton(f'{i[5]}, {i[6]}, {i[2]}',
                                                       callback_data=f'myposts{str(n)}')
                    markup.add(p)
                    n += 1
                await MyPosts.choice.set()
                await bot.send_message(message.from_user.id, 'Выберите одну публикацию', reply_markup=markup)
            else:
                await bot.send_message(message.from_user.id, "У вас нету публикаций")


# --------------------------------------
        #my chats 1
        elif message.text == 'Мои чаты':
            markup = types.InlineKeyboardMarkup()
            chats = db.find_chat_byid(message.from_user.id)
            if chats:
                n = 0
                for i in chats:
                    p = types.InlineKeyboardButton(f'Чат №{i[0]}',
                                                   callback_data=f'mychats{str(n)}')
                    markup.add(p)
                    n += 1
                await MyChats.chatschoice.set()
                await bot.send_message(message.from_user.id, 'Выберите один чат', reply_markup=markup)
            else:
                await message.answer("Вас нету ни в одном чате")
# -----------------------
        #becomecomp 1
        elif message.text == "Стать выполнителем":
            if not db.getcompleter(message.from_user.id):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add('Отменить')

                await bot.send_message(message.chat.id, "***Введите свое настоящее имя***\n\nЧтобы отменить, нажмите ***Отменить***", reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
                await BecomeCompleter.name.set()
            else:
                await message.answer('Вы уже отправили заявку!')
# ---------------------------
        # my bal 1
        elif message.text == 'Мои деньги':
            if db.getcompleter(message.from_user.id):
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton('Вывести деньги', callback_data='withdraw')
                markup.add(item1)
                completer = db.getcompleter(message.from_user.id)[0]
                await message.answer(f'На вашем балансе {completer[7]} грн\nПостов выполнено: {completer[8]}' if completer[8] else f'На вашем балансе {completer[7]} грн', reply_markup=markup)
            else:
                await message.answer('У вас нету средств')
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

    await bot.send_message(message.from_user.id, f"Напишите краткое описание того, что нужно сделать", reply_markup=markup)
    await NewPost.next()

# New Post 4
@dp.message_handler(state=NewPost.maintext)
async def newposttext(message: types.Message, state: FSMContext):
    #cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Договорная', 'Отменить')
        # DATA
        async with state.proxy() as data:
            data["maintext"] = message.text

        await bot.send_message(message.from_user.id, f"Назвите цену или нажмите «Договорная» \n\nНапример, чтобы указать цену в 100 грн, введите «100»", reply_markup=markup)
        await NewPost.next()

# New Post 5
@dp.message_handler(state=NewPost.price)
async def newpostprice(message: types.Message, state: FSMContext):
    # cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:
        async with state.proxy() as data:
            if data["protection"] == 'protected':
                if message.text == "Договорная":
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add('Готово', 'Отменить')
                    # DATA

                    data["price"] = message.text
                    data["mediaid"] = []
                    data["docid"] = []
                    await bot.send_message(message.from_user.id, f"Теперь добавьте файл или фото, ассоциированый с заданием, затем нажмите «Готово»", reply_markup=markup)
                    await NewPost.next()

                elif message.text.isnumeric():

                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add('Готово', 'Отменить')

                    # DATA

                    data["price"] = message.text
                    data["mediaid"] = []
                    data["docid"] = []
                    await bot.send_message(message.from_user.id, f"Теперь добавьте файл или фото, ассоциированый с заданием, затем нажмите «Готово»", reply_markup=markup)
                    await NewPost.next()

                else:
                    await bot.send_message(message.from_user.id, f"Ошибка в указании цены, правильно указать цену без текста\nНапример, чтобы указать цену в 100 грн, введите «100»")
            else:

                if message.text == "Договорная":
                    data["price"] = message.text
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add('Опубликовать', 'Отменить')

                    #preview ORDINARY
                    post = Post(active="Активный", author=message.from_user.id, completer="Нету",
                                theme=data["theme"], maintext=data["maintext"], price=data["price"],
                                mediaid='', docid='', protection=data["protection"])
                    data["post"] = post

                    # send
                    await bot.send_message(message.from_user.id,
                                           "Перед тем как опубликовать, если вы хотите изменить что-либо, просто измените сообщения которые вы отправили ранее. Затем, нажмите <b>Опубликовать</b>",
                                           reply_markup=markup, parse_mode=types.ParseMode.HTML)
                    await bot.send_message(message.from_user.id, f"<b>ПРЕВЬЮ ПОСТА</b>\n{post.tostring()}",
                                           parse_mode=types.ParseMode.HTML)
                    await NewPost.next()
                    await NewPost.next()
                elif message.text.isnumeric():
                    data["price"] = message.text
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add('Опубликовать', 'Отменить')

                    # preview ORDINARY
                    post = Post(active="Активный", author=message.from_user.id, completer="Нету",
                                theme=data["theme"], maintext=data["maintext"], price=data["price"],
                                mediaid='', docid='', protection=data["protection"])
                    data["post"] = post

                    # send
                    await bot.send_message(message.from_user.id,
                                           "Перед тем как опубликовать, если вы хотите изменить что-либо, просто измените сообщения которые вы отправили ранее. Затем, нажмите <b>Опубликовать</b>",
                                           reply_markup=markup, parse_mode=types.ParseMode.HTML)
                    await bot.send_message(message.from_user.id, f"<b>ПРЕВЬЮ ПОСТА</b>\n{post.tostring()}",
                                           parse_mode=types.ParseMode.HTML)
                    await NewPost.next()
                    await NewPost.next()
                else:
                    await bot.send_message(message.from_user.id, f"Ошибка в указании цены, правильно указать цену без текста\nНапример, чтобы указать цену в 100 грн, введите «100»")

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
    async with state.proxy() as data:

        # cancel
        if message.text == "Отменить":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add('Новый пост')
            markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
            await state.finish()
            await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
        else:
            if message.text == "Готово":
                media = types.MediaGroup()
                docs = []


                data["doclink"] = []
                for i in data["mediaid"]:
                    media.attach_photo(photo=i)
                for j in data["docid"]:
                    filemessagedoc = await bot.send_document(filebotid, j)
                    docs.append(hide_link(filemessagedoc.url))
                    data["doclink"].append(hide_link(filemessagedoc.url))
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add('Опубликовать', 'Отменить')


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
                await bot.send_message(message.from_user.id, "Перед тем как опубликовать, если вы хотите изменить что-либо, просто измените сообщения которые вы отправили ранее. Затем, нажмите <b>Опубликовать</b>", reply_markup=markup, parse_mode=types.ParseMode.HTML)
                await bot.send_message(message.from_user.id, f"<b>ПРЕВЬЮ ПОСТА</b>\n{post.tostring()}", parse_mode=types.ParseMode.HTML)
                await NewPost.next()

# New post 8 Final, publish to main channel
@dp.message_handler(state=NewPost.publish)
async def newpostpublish(message: types.Message, state: FSMContext):

    # cancel
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:
        if message.text == 'Опубликовать':
            markup = types.InlineKeyboardMarkup()
            # chat1

            async with state.proxy() as data:
                postid = db.publishpost(data["post"])

                link = await get_start_link(str(postid), encode=True)
                if data["protection"] == "protected":
                    item1 = types.InlineKeyboardButton('Беру', url=link)
                    markup.add(item1)
                    publishedmessage = await bot.send_message(publicationbotid, data['post'].tostring(), reply_markup=markup, parse_mode=types.ParseMode.HTML)

                else:
                    publishedmessage = await bot.send_message(publicationbotid, f"{data['post'].tostring()}\nКонтакт: <a href='https://telegram.me/{message.from_user.username}'>{message.from_user.first_name}</a>", reply_markup=markup, parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)

                #superuser
                encoded_data = urllib.parse.urlencode({
                    "user": message.from_user.id,
                    "postid": postid
                })
                url = f"https://telegram.me/{message.from_user.username}"
                markup2 = types.InlineKeyboardMarkup()
                item2 = types.InlineKeyboardButton('Удалить', callback_data=f"admindelete{encoded_data}")
                item3 = types.InlineKeyboardButton('Контакт пользователя', url=url)
                markup2.add(item2, item3)
                msgtoadmin = await bot.send_message(supergroupid, data["post"].tostring(), parse_mode=types.ParseMode.HTML, reply_markup=markup2)

                #linkhandle
                linktopublished = publishedmessage.url
                db.givepostalink(postid, linktopublished)


            #user

            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup2.add('Новый пост')
            markup2.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
            await bot.send_message(message.from_user.id, f"Отлично, пост готов и опубликован на основном канале {hide_link(linktopublished)}", reply_markup=markup2, parse_mode=types.ParseMode.HTML)
            await state.finish()

# My posts2
@dp.callback_query_handler(lambda call: call.data.startswith('myposts'), state=MyPosts.choice)
async def mypostsshow(call: types.CallbackQuery, state: FSMContext):

    ind = str(call.data).replace('myposts', '')
    post = db.findallposts(call.message.chat.id)[int(ind)]

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Удалить', callback_data='postdelete')
    item2 = types.InlineKeyboardButton('Назад', callback_data='postback')
    markup.add(item1, item2)
    if post[4] != 'protected' and post[2] == 'Активный':
        item3 = types.InlineKeyboardButton('Отметить как выполненое', callback_data='reglarpost')
        markup.add(item3)
    async with state.proxy() as data:
        data["post"] = post
    await bot.edit_message_text(f"<b>Статус:</b> {post[2]}\n<b>Выполнитель:</b> {db.getcompleter(post[3])[0][2] if db.getcompleter(post[3]) else post[3]}\n<b>Тип поста:</b> {'Защищённый пост' if post[4]=='protected' else 'Обычный пост'}\n<b>Тема:</b> {post[5]}\n<b>Задание:</b> {post[6]}\n<b>Цена:</b> {post[7]}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.HTML)
    await MyPosts.next()

# My posts 3
@dp.callback_query_handler(lambda call: call.data in ['postdelete', 'postback', 'reglarpost'], state=MyPosts.deleteorback)
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
    elif call.data == 'reglarpost':
        async with state.proxy() as data:
            post = data['post']
        db.updateactivestatus(post[0], 'Выполнено')
        postinst = Post('Выполнено', post[2], post[3], post[4], post[5], post[6], post[7], '', '')
        message_id = re.search(r'/(\d+)$', post[10]).group(1)
        await bot.edit_message_text('Отмечено как выполнено', call.message.chat.id, call.message.message_id)
        await bot.edit_message_text(postinst.tostring(), publicationbotid, message_id, parse_mode=types.ParseMode.HTML)

# I take post 2
@dp.callback_query_handler(lambda call: call.data.startswith('takeapprove') or call.data.startswith('takenot'), state='*')
async def approvingproc(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('takeapprove'):

        #data
        encodeddata = call.data[11:]
        decoded_data = urllib.parse.parse_qs(encodeddata)

        completer = decoded_data["completer"][0]
        postid = decoded_data["postid"][0]

        post = db.findpost(postid)[0]
        postlink = post[10]

        if post[11]:
           await call.answer("У вас уже есть активная сделка по этому посту")
        else:
            # get link for chat
            markup = types.InlineKeyboardMarkup()
            if db.getfreechat():
                freechat = db.getfreechat()[0][1]

                #days=365 * 5
                future_date = datetime.now() + timedelta(days=365 * 5)
                invitelink = await bot.create_chat_invite_link(freechat)
                # db chat update
                db.update_chat(freechat, completer, call.from_user.id, post[0])
    
                item1 = types.InlineKeyboardButton('Открыть чат', url=f"{invitelink.invite_link}")
                markup.add(item1)
                userinvite = await bot.edit_message_text('***Вы приняли заявку***\n\nТеперь вы можете открыть чат', call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
                completerinvite = await bot.send_message(completer, f"<b>Пользователь</b> принял вашу заявку {hide_link(postlink)}", parse_mode=types.ParseMode.HTML, reply_markup=markup)
    
                # db chat update
                db.update_chat_links(freechat, userinvite.message_id, completerinvite.message_id)
                db.add_chat_to_post(post[0], freechat)
            else: 
                await call.answer("Все чаты заняты")
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
    integer_list = [int(item[0]) for item in db.getalloccupiedchats()]
    if message.chat.id in integer_list:
        chatdetails = db.getchatdetails(message.chat.id)[0]

        post = db.findpost(chatdetails[4])[0]

        completer = db.getcompleter(chatdetails[2])[0]
        user = chatdetails[3]

        completer_member = await message.chat.get_member(completer[1])
        user_member = await message.chat.get_member(user)

        if types.ChatMember.is_chat_member(completer_member) and types.ChatMember.is_chat_member(user_member):
            medialinks = post[8]
            doclinks = eval(post[9])

            await message.answer(
                f"Два участника сделки присоеденились\n\nЗаказчик: {db.finduserbyid(user)[0][2]}\nВыполняющий: {completer[2]}\n\nЧтобы оплатить или позвать администратора, нажмите на /menu",
                parse_mode=types.ParseMode.MARKDOWN_V2)
            messagetopin = await bot.send_message(message.chat.id, f"{post[5]}\n{post[6]}")
            await bot.pin_chat_message(message.chat.id, messagetopin.message_id)

            if medialinks:
                await bot.send_message(message.chat.id, f"{post[8]}", parse_mode=types.ParseMode.HTML)
            if doclinks:
                for i in doclinks:
                    await bot.send_message(message.chat.id, i, parse_mode=types.ParseMode.HTML)



        elif types.ChatMember.is_chat_member(completer_member):

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Позвать собеседника', callback_data=f'pozvatklienta{user}')
            markup.add(item1)

            await bot.send_message(message.chat.id, "Другой участник сделки еще не присоединился", reply_markup=markup)
        elif types.ChatMember.is_chat_member(user_member):

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Позвать собеседника', callback_data=f'pozvatcompleter{completer}')
            markup.add(item1)

            await bot.send_message(message.chat.id, "Другой участник сделки еще не присоединился", reply_markup=markup)

        else:
            if message.from_user.id != superuserid:
                await message.chat.kick(message.from_user.id)
                await bot.unban_chat_member(message.chat.id, message.from_user.id)
# i take post pozvat
@dp.callback_query_handler(lambda call: call.data.startswith('pozvatklienta') or call.data.startswith('pozvatcompleter'), state='*')
async def pozvat(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('pozvatklienta'):
        klientnumber = call.data[13:]
        user_member = await call.message.chat.get_member(klientnumber)
        if not types.ChatMember.is_chat_member(user_member):
            await call.answer(cache_time=60)
            await call.message.answer("Вы позвали клиента")
            await bot.send_message(klientnumber, f"Выполнитель вашего поста уже зашёл и ждёт вас")
    elif call.data.startswith('pozvatcompleter'):
        completernumber = call.data[15:]
        completer_member = await call.message.chat.get_member(completernumber)
        if not types.ChatMember.is_chat_member(completer_member):
            await call.answer(cache_time=60)
            await call.message.answer("Вы позвали выполнителя")
            await bot.send_message(completernumber, f"Клиент уже зашёл и ждёт вас")

# My chats 2
@dp.callback_query_handler(lambda call: call.data.startswith('mychats'), state=MyChats.chatschoice)
async def mychatsshow(call: types.CallbackQuery, state: FSMContext):
    # data
    num = int(call.data[7:])
    chat = db.find_chat_byid(call.message.chat.id)[num]
    user = db.finduserbyid(chat[2])
    completer = db.getcompleter(chat[3])[0]
    invitelink = await bot.create_chat_invite_link(chat[1])
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Перейти', url=invitelink.invite_link)
    item2 = types.InlineKeyboardButton('Назад', callback_data='mychatback')
    markup.add(item1, item2)

    async with state.proxy() as data:
        data["chat"] = chat
    await MyChats.next()
    await bot.edit_message_text(f"<b>Номер чата:</b> {chat[0]}\n<b>Выполнитель:</b> {completer[2]}\n<b>Клиент:</b> {user[0][2]}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.HTML)
#superuser2
@dp.callback_query_handler(lambda call: call.data.startswith('admindelete'))
async def admindelete(call: types.CallbackQuery, state: FSMContext):

    encodeddata = call.data[11:]
    decoded_data = urllib.parse.parse_qs(encodeddata)

    userid = decoded_data["user"][0]
    postid = decoded_data["postid"][0]

    post = db.findpost(postid)[0]

    if post[11]:
        chat = db.chat_byid(post[11])[0]
        db.clear_chat(post[11])

        await bot.unpin_all_chat_messages(post[11])

        if chat[2] != superuserid:
            await bot.kick_chat_member(post[11], chat[2])
            await bot.unban_chat_member(post[11], chat[2])
        if chat[3] != superuserid:
            await bot.kick_chat_member(post[11], chat[3])
            await bot.unban_chat_member(post[11], chat[3])

    db.deletepost(post[0])
    message_id = re.search(r'/(\d+)$', post[10]).group(1)
    await bot.delete_message(publicationbotid, message_id)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(userid, "Администратор удалил один из ваших постов")


#superuser3
@dp.callback_query_handler(lambda call: call.data.startswith('calladminchat'))
async def admincall(call: types.CallbackQuery, state: FSMContext):
    encodeddata = call.data[13:]
    decoded_data = urllib.parse.parse_qs(encodeddata)

    chatid = decoded_data["chatid"][0]
    chat = db.chat_byid(call.message.chat.id)[0]
    post = db.findpost(chat[4])[0]
    invitelink = await bot.create_chat_invite_link(post[11])

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Войти', url=f"{invitelink.invite_link}")
    markup.add(item1)

    await bot.send_message(superuserid, f"Вас позвали в чат", reply_markup=markup)
    await call.answer(cache_time=60)
    await bot.send_message(call.message.chat.id, 'Вы позвали администратора')


@dp.callback_query_handler(lambda call: call.data.startswith('chatdealrefuse'))
async def chatdealrefuse(call: types.CallbackQuery, state: FSMContext):
    encodeddata = call.data[14:]
    decoded_data = urllib.parse.parse_qs(encodeddata)

    chat = db.chat_byid(call.message.chat.id)[0]
    post = db.findpost(chat[4])[0]

    async with state.proxy() as data:
        data['caller'] = call.message.from_user.id

    await bot.send_message(call.message.chat.id, "***Вы уверены, что вы хотите отменить сделку?***\n\nНапишите: `Да, я хочу отменить сделку`\n\nТекст можно скопировать, нажав на него\n***Важно*** После отмены чат будет удалён", parse_mode=types.ParseMode.MARKDOWN_V2)
    await CancelDeal.ackgnowledgment.set()


@dp.message_handler(state=CancelDeal.ackgnowledgment)
async def canceldealack(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        caller = data['caller']
    if message.from_user.id == caller:
        if message.text == "Да, я хочу отменить сделку":
            chat = db.chat_byid(message.chat.id)[0]

            #chatdeletion
            db.clearpostchatid(chat[4])
            db.clear_chat(message.chat.id)

            await bot.delete_message(chat_id=chat[2], message_id=chat[6])
            await bot.delete_message(chat_id=chat[3], message_id=chat[5])

            await message.answer("Сделка отменена")
            await state.finish()
            await bot.unpin_all_chat_messages(message.chat.id)

            if chat[2] != superuserid:
                await bot.kick_chat_member(message.chat.id, chat[2])
                await bot.unban_chat_member(message.chat.id, chat[2])
            if chat[3] != superuserid:
                await bot.kick_chat_member(message.chat.id, chat[3])
                await bot.unban_chat_member(message.chat.id, chat[3])
        else:
            await message.answer("Сделка не отменена")
            await state.finish()

#becomecomp 2
@dp.message_handler(state=BecomeCompleter.name)
async def becomecompone(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Отменить')

        async with state.proxy() as data:
            data["name"] = message.text

        await message.answer("Введите почту", reply_markup=markup)
        await BecomeCompleter.next()
#becomecomp 2
@dp.message_handler(state=BecomeCompleter.email)
async def becomecomponeemail(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Отменить')

        async with state.proxy() as data:
            data["email"] = message.text

        await message.answer("Введите дату рождения", reply_markup=markup)
        await BecomeCompleter.next()
#becomecomp 3
@dp.message_handler(state=BecomeCompleter.date)
async def becomecomponephone(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = KeyboardButton(text="Поделится номером телефона", request_contact=True)
        markup.add('Отменить', button)

        async with state.proxy() as data:
            data["date"] = message.text

        await bot.send_message(message.from_user.id, "***Введите номер телефона***\n\nНажмите кнопку ***Поделится номером телефона***", reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
        await BecomeCompleter.next()
#becomecomp 4
@dp.message_handler(content_types=[types.ContentType.CONTACT, 'text'], state=BecomeCompleter.phone)
async def handle_contact(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Подтвердить', 'Отменить')

        if type(message.contact) == types.contact.Contact:
            async with state.proxy() as data:
                data["phone"] = message.contact.phone_number
        else:
            async with state.proxy() as data:
                data["phone"] = message.text


        await bot.send_message(message.from_user.id, "Чтобы оставить заявку, нажмите ***Подтверить***", reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
        await BecomeCompleter.next()
#becomecomp 5 final
@dp.message_handler(state=BecomeCompleter.ack)
async def becomecomponephone(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add('Новый пост')
        markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
        await state.finish()
        await bot.send_message(message.from_user.id, "Отменено", reply_markup=markup)
    else:
        async with state.proxy() as data:
            db.createcompleter(message.from_user.id, data["name"], data["email"], data["date"], data["phone"], "no", 0, 0)
            #send to superuser

            encoded_data = urllib.parse.urlencode({
                "completer": message.chat.id
            })

            url = f"https://telegram.me/{message.from_user.username}"
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Подтвердить", callback_data=f"compstatusaccept{encoded_data}")
            item2 = types.InlineKeyboardButton("Отклонить", callback_data=f"compstatusreject{encoded_data}")
            markup.add(item1, item2)

            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup2.add('Новый пост')
            markup2.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')

            await bot.send_message(superuserid, f"Заявка от <a href='{url}'>{message.from_user.first_name}</a>\n\nДанные\n<b>Настоящее имя: </b>{data['name']}\n<b>Почта: </b>{data['email']}\n<b>Дата рождения: </b>{data['date']}\n<b>Номер телефона: </b>{data['phone']}", reply_markup=markup, parse_mode=types.ParseMode.HTML)
        await bot.send_message(message.from_user.id,
                               "Ваша заявка принята и будет рассмотрена администратором. После этого вы сможете выполнять публикации клиентов", reply_markup=markup2)
        await state.finish()
#superuserapprovecomp
@dp.callback_query_handler(lambda call: call.data.startswith('compstatusaccept') or call.data.startswith('compstatusreject'))
async def admincallll(call: types.CallbackQuery, state: FSMContext):

    if call.data.startswith('compstatusaccept'):
        encodeddata = call.data[16:]
        decoded_data = urllib.parse.parse_qs(encodeddata)

        completer = decoded_data["completer"][0]
        db.updatecompleterstatus(completer, 'yes')

        await bot.edit_message_text("Заявка принята", call.message.chat.id, call.message.message_id)
        await bot.send_message(completer, "Администратор принял вашу заявку. Теперь вы можете выполнять публикации клиентов")

    elif call.data.startswith('compstatusreject'):
        encodeddata = call.data[16:]
        decoded_data = urllib.parse.parse_qs(encodeddata)

        completer = decoded_data["completer"][0]

        await bot.edit_message_text("Заявка отклонена", call.message.chat.id, call.message.message_id)
        await bot.send_message(completer, "Администратор отклонил вашу заявку")

@dp.callback_query_handler(lambda call: call.data.startswith('payprice'))
async def pay(call: types.CallbackQuery, state: FSMContext):

    encodeddata = call.data[8:]

    chat = db.chat_byid(call.message.chat.id)[0]
    post = db.findpost(chat[4])[0]
    if type(post[7]) == float:
        price = int(post[7]) + 5
        invitelink = await bot.create_chat_invite_link(call.message.chat.id)
        amount = int(price) * 100
        order_desc = 'TurtleBot payment'
        response_url = invitelink.invite_link
        currency = 'UAH'
        payid = db.createpayment(price, post[0])
        order_id = payid + 1
        db.giveorderid(payid, order_id)
        result = api.checkout(order_id, amount, order_desc, response_url, currency)

        if result.get('response') and 'error_message' in result['response']:
            error_message = result['response']['error_message']
            print(error_message)
            await bot.send_message("Ошибка, попробуйте ещё раз")
        else:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Оплатить", url=result['response']['checkout_url'])
            item2 = types.InlineKeyboardButton("Поменять цену", callback_data=f"changeprice{encodeddata}")
            curstatus = api.order_status(str(order_id))['response']['order_status']

            db.updateorderstatus(payid, curstatus)
            markup.add(item1, item2)
            await bot.edit_message_text(f"{db.finduserbyid(chat[3])[0][2]}, чтобы оплатить сделку, вам нужно нажать кнопку <b>Оплатить</b> и выбрать удобный способ оплаты\n\nПосле успешной оплаты прийдёт уведомление и {db.getcompleter(chat[2])[0][2]} может начать выполнять задание\n\n<b>К оплате:</b> {price} грн\n<b>Комиссия: 5 грн</b>", call.message.chat.id, call.message.message_id, parse_mode=types.ParseMode.HTML, reply_markup=markup)

        async def check_payment_status():
            while True:
                latest_payid = db.payidbypost(post[0])[0][0]
                if payid == latest_payid:
                    condition = db.getpaymentbyid(payid)[0][2]

                    if condition == 'created':
                        checking = api.order_status(str(order_id))['response']['order_status']
                        if checking == 'approved':
                            await bot.delete_message(call.message.chat.id, call.message.message_id)
                            db.updateorderstatus(payid, checking)
                            await bot.send_message(call.message.chat.id,
                                                   f"<b>Платёж проведён успешно</b>\n\n{db.getcompleter(chat[2])[0][2]} может приступать к выполнению",
                                                   parse_mode=types.ParseMode.HTML)
                            db.updatepostcompleter(post[0], chat[2])
                            break
                    await asyncio.sleep(2)
                else:
                    break

        asyncio.create_task(check_payment_status())


    else:
        await call.message.answer("Нажмите ***Поменять цену*** и укажите новую цену", parse_mode=types.ParseMode.MARKDOWN_V2)

@dp.callback_query_handler(lambda call: call.data.startswith('mychatback'), state=MyChats.backodelete)
async def mychatback(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    chats = db.find_chat_byid(call.from_user.id)
    if chats:
        n = 0
        for i in chats:
            p = types.InlineKeyboardButton(f'Чат №{i[0]}',
                                           callback_data=f'mychats{str(n)}')
            markup.add(p)
            n += 1
        await MyChats.chatschoice.set()
        await bot.edit_message_text('Выберите один чат', call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        await call.answer("Вас нету ни в одном чате")
@dp.callback_query_handler(lambda call: call.data.startswith('changeprice'))
async def changeprice(call: types.CallbackQuery):
    chatindb = db.chat_byid(call.message.chat.id)[0]
    post = db.findpost(chatindb[4])[0]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Отменить")
    await bot.delete_message(call.message.chat.id, call.message.message_id)

    await bot.send_message(call.message.chat.id, f"<b>СТАРАЯ ЦЕНА:</b> {f'{int(post[7])} грн' if type(post[7]) == float else 'Договорная'}\nНазвите новую цену или нажмите <b>Отменить</b>\n\nНапример, чтобы указать цену в 100 грн, введите «100»", reply_markup=markup, parse_mode=types.ParseMode.HTML)
    await ChatChangePrice.changingprice.set()
@dp.message_handler(state=ChatChangePrice.changingprice)
async def changingp(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        encoded_data = urllib.parse.urlencode({
            "user": message.from_user.id,
            "chatid": message.chat.id,
        })

        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("Поменять цену", callback_data=f"changeprice{encoded_data}")
        item2 = types.InlineKeyboardButton("Оплатить", callback_data=f"payprice{encoded_data}")
        item3 = types.InlineKeyboardButton("Позвать администратора", callback_data=f"calladminchat{encoded_data}")
        item4 = types.InlineKeyboardButton("Отменить сделку", callback_data=f"chatdealrefuse{encoded_data}")

        markup.add(item1, item2, item3, item4)

        m2 = types.ReplyKeyboardRemove()
        delmes = await bot.send_message(message.chat.id, "Загрузка...", reply_markup=m2)
        await bot.delete_message(message.chat.id, delmes.message_id)
        await bot.send_message(message.chat.id, "Нажмите на кнопку из меню", reply_markup=markup)
        await state.finish()
    elif message.text.isnumeric():
        chatindb = db.chat_byid(message.chat.id)[0]
        post = db.findpost(chatindb[4])[0]
        db.updateprice(post[0], message.text)

        #filler
        encoded_data = urllib.parse.urlencode({
            "user": message.from_user.id,
            "chatid": message.chat.id,
        })

        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("Поменять цену", callback_data=f"changeprice{encoded_data}")
        item2 = types.InlineKeyboardButton("Оплатить", callback_data=f"payprice{encoded_data}")
        item3 = types.InlineKeyboardButton("Позвать администратора", callback_data=f"calladminchat{encoded_data}")
        item4 = types.InlineKeyboardButton("Отменить сделку", callback_data=f"chatdealrefuse{encoded_data}")

        markup.add(item1, item2, item3, item4)

        await bot.send_message(message.chat.id, f"Цена обновлена, новая цена: {int(db.findpost(post[0])[0][7])} грн")
        await bot.send_message(message.chat.id, "Нажмите на кнопку из меню", reply_markup=markup)
        await state.finish()
    else:
        await bot.send_message(message.chat.id,
                               f"Ошибка в указании цены, правильно указать цену без текста\nНапример, чтобы указать цену в 100 грн, введите «100»")

#dealcomplete
@dp.callback_query_handler(lambda call: call.data.startswith('dealcomplete'))
async def dealcompleting(call: types.CallbackQuery, state: FSMContext):
    chat = db.chat_byid(call.message.chat.id)[0]
    post = db.findpost(chat[4])[0]

    usermember = await bot.get_chat_member(call.message.chat.id, chat[3])
    await DealCompleting.completea.set()
    await bot.edit_message_text(f"{md.bold('Вы уверенны, что хотите завершить сделку?')}\n\nЗавершение сделки означает, что заказчик получил решение и оно его устраивает\nДеньги за сделку получит выполнитель\n\n{md.link(usermember.user.first_name, 'https://telegram.me/' + usermember.user.username)} чтобы завершить сделку, напишите этот текст: \n\n`Да, я абсолютно уверен`\nНажмите, чтобы скопировать\n\n{md.bold('Внимание!')}\nПосле завершения сделки чат будет удалён\n{md.link(usermember.user.first_name, 'https://telegram.me/' + usermember.user.username)}, сохраните решение заранее", call.message.chat.id, call.message.message_id, parse_mode=types.ParseMode.MARKDOWN_V2, disable_web_page_preview=True)

@dp.message_handler(state=DealCompleting.completea)
async def changingp(message: types.Message, state: FSMContext):
    chat = db.chat_byid(message.chat.id)[0]
    post = db.findpost(chat[4])[0]

    if message.from_user.id == chat[3]:
        if message.text == "Да, я абсолютно уверен":
            #clear the chat. give money to completer, give +1 post for completer, ask to rate the completer. change post status to Выполнено
            chat = db.chat_byid(message.chat.id)[0]
            completer = db.getcompleter(chat[2])[0]
            newcompbal = completer[7] + post[7]
            newcompposts = completer[8] + 1
            #give mone
            db.updcompbal(chat[2], newcompbal)
            db.updatecompleterposts(chat[2], newcompposts)
            db.clear_chat(message.chat.id)

            #change state to complete
            db.updateactivestatus(post[0], 'Выполнено')

            postinst = Post('Выполнено', post[2], post[3], post[4], post[5], post[6], int(post[7]), '', '')
            message_id = re.search(r'/(\d+)$', post[10]).group(1)
            await bot.edit_message_text(postinst.tostring(), publicationbotid, message_id, parse_mode=types.ParseMode.HTML)

            await bot.unpin_all_chat_messages(message.chat.id)

            if chat[2] != superuserid:
                await bot.kick_chat_member(message.chat.id, chat[2])
                await bot.unban_chat_member(message.chat.id, chat[2])
            if chat[3] != superuserid:
                await bot.kick_chat_member(message.chat.id, chat[3])
                await bot.unban_chat_member(message.chat.id, chat[3])


            await state.finish()
            await message.answer('Сделка завершена')
        else:
            await message.answer('Сделка продолжается')
            await state.finish()
@dp.callback_query_handler(lambda call: call.data == 'withdraw')
async def completwithdraw(call: types.CallbackQuery, state: FSMContext):
    print(db.getcompleter(call.message.chat.id)[0][7])
    if db.getcompleter(call.message.chat.id)[0][7]>0:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call.message.chat.id, "Введите номер карты, на которую будет совершен перевод")
        await Withdrawing.entercard.set()
    else:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call.message.chat.id, "У вас нету средств")
@dp.message_handler(state=Withdrawing.entercard)
async def withcheck(message: types.Message, state: FSMContext):
    completer = db.getcompleter(message.from_user.id)[0]
    url = f"https://telegram.me/{message.from_user.username}"
    print(completer)
    encoded_data = urllib.parse.urlencode({
        "completerid": message.chat.id,
    })
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Оплата завершена', callback_data=f'withsuccess{encoded_data}')
    item2 = types.InlineKeyboardButton('Контакт выполнителя', url=url)
    markup.add(item1, item2)

    await bot.send_message(message.chat.id, f'{md.bold("Заявка на вывод денег отправлена")}\n\nАдминистратор проверит заявку в течении 24 часа и отправит деньги на карту', parse_mode=types.ParseMode.MARKDOWN_V2)
    await bot.send_message(superuserid, f"<b>Заявка на вывод денег от {completer[2]}</b>\nДанные выполнителя: {completer}\n\nУказанная карта для перевода: {message.text}", parse_mode=types.ParseMode.HTML, reply_markup=markup)
    await state.finish()
@dp.callback_query_handler(lambda call: call.data.startswith('withsuccess'))
async def oplacheno(call: types.CallbackQuery, state: FSMContext):


    encodeddata = call.data[11:]
    decoded_data = urllib.parse.parse_qs(encodeddata)
    completer = db.getcompleter(decoded_data['completerid'][0])[0]

    db.updcompbal(completer[1], 0)

    await bot.send_message(completer[1], "Администратор отправил вам деньги на карту")
    await bot.edit_message_text(f"{completer[2]} оплата завершена\nНовый баланс выполнителя: {db.getcompleter(decoded_data['completerid'][0])[0][7]}", call.message.chat.id, call.message.message_id)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)