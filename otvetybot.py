import re
import urllib.parse

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
chatbotids = [-1001595908456, -1001800064192, -1001801606004, -1001605913621]
occupiedchats = []
# ID superuser
superuserid = 444768059
supergroupid = -1001962874240
# -------------------------------------
for i in chatbotids:
    db.createchat(i)
for j in db.getalloccupiedchats():
    occupiedchats.append(j[1])
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
    phone = State()
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
# USER SIDE ----------------------------------------------------
# start handler - give menu
@dp.message_handler(commands=['start', 'menu'], state='*')
async def command_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    payload = decode_payload(args)
    # I take post 1 ------------------------------------------------------------------------------
    if payload:
        post = db.findpost(payload)[0]
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
        if message.chat.type == 'private':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add('Новый пост')
            markup.add('Стать выполнителем', 'Мои чаты', 'Мои посты', 'Мои деньги')
            db.makeuser(message.from_user.id, message.from_user.full_name)


            await message.answer(f'Здравствуйте, это бот паблика «TurtleUA», выберите одно действие из меню.', reply_markup=markup)
        elif message.chat.id in occupiedchats:

            #chatmenu1
            encoded_data = urllib.parse.urlencode({
                "user": message.from_user.id,
                "chatid": message.chat.id,
            })

            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton("Поменять цену", callback_data="changeprice")
            item2 = types.InlineKeyboardButton("Оплатить", callback_data="payprice")
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
        #becomecomp 1
        elif message.text == "Стать выполнителем":

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Отменить')

            await bot.send_message(message.chat.id, "***Введите свое настоящее имя***\n\nЧтобы отменить, нажмите ***Отменить***", reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
            await BecomeCompleter.name.set()

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
        if message.text == "Договорная":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Готово', 'Отменить')
            # DATA
            async with state.proxy() as data:
                data["price"] = message.text
                data["mediaid"] = []
                data["docid"] = []
            await bot.send_message(message.from_user.id, f"Теперь добавьте файл или фото, ассоциированый с заданием, затем нажмите «Готово»", reply_markup=markup)
            await NewPost.next()

        elif message.text.isnumeric():

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Готово', 'Отменить')

            # DATA
            async with state.proxy() as data:
                data["price"] = message.text
                data["mediaid"] = []
                data["docid"] = []
            await bot.send_message(message.from_user.id, f"Теперь добавьте файл или фото, ассоциированый с заданием, затем нажмите «Готово»", reply_markup=markup)
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

                item1 = types.InlineKeyboardButton('Беру', url=link)
                markup.add(item1)

                publishedmessage = await bot.send_message(publicationbotid, data["post"].tostring(), reply_markup=markup, parse_mode=types.ParseMode.HTML)

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
            freechat = chatbotids.pop()
            occupiedchats.append(freechat)


            invitelink = await bot.create_chat_invite_link(freechat, expire_date=999999999999999)
            # db chat update
            db.update_chat(freechat, completer, call.from_user.id, post[0])
            item1 = types.InlineKeyboardButton('Открыть чат', url=f"{invitelink.invite_link}")
            markup.add(item1)
            userinvite = await bot.edit_message_text('***Вы приняли заявку***\n\nТеперь вы можете открыть чат', call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
            completerinvite = await bot.send_message(completer, f"<b>Пользователь</b> принял вашу заявку {hide_link(postlink)}", parse_mode=types.ParseMode.HTML, reply_markup=markup)

            # db chat update
            db.update_chat_links(freechat, userinvite.message_id, completerinvite.message_id)
            db.add_chat_to_post(post[0], freechat)
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
        chatdetails = db.getchatdetails(message.chat.id)[0]
        post = db.findpost(chatdetails[4])[0]
        completer = chatdetails[2]
        user = chatdetails[3]
        completer_member = await message.chat.get_member(completer)
        user_member = await message.chat.get_member(user)

        if types.ChatMember.is_chat_member(completer_member) and types.ChatMember.is_chat_member(user_member):
            medialinks = post[8]
            doclinks = eval(post[9])

            await message.answer(
                f"Два участника сделки присоеденились\n\nЗаказчик: {db.finduserbyid(user)[0][2]}\nВыполняющий: {db.finduserbyid(completer)[0][2]}\n\nЧтобы оплатить или позвать администратора, нажмите на /menu",
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

            await bot.send_message(message.chat.id, "Выполнитель зашёл первым", reply_markup=markup)
        elif types.ChatMember.is_chat_member(user_member):

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Позвать собеседника', callback_data=f'pozvatcompleter{completer}')
            markup.add(item1)

            await bot.send_message(message.chat.id, "Заказчик работы зашёл первым", reply_markup=markup)

        else:
            if not message.from_user.id == superuserid:
                await message.chat.kick(message.from_user.id)
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
    completer = db.finduserbyid(chat[3])

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Удалить', callback_data='mychatdelete')
    item2 = types.InlineKeyboardButton('Назад', callback_data='mychatback')
    markup.add(item1, item2)

    async with state.proxy() as data:
        data["chat"] = chat

    await bot.edit_message_text(f"<b>Номер чата:</b> {chat[0]}\n<b>Выполнитель:</b> {completer[0][2]}\n<b>Клиент:</b> {user[0][2]}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode=types.ParseMode.HTML)
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
        occupiedchats.remove(post[11])
        chatbotids.append(post[11])


        await bot.unpin_all_chat_messages(post[11])

        if chat[2] != superuserid:
            await bot.kick_chat_member(post[11], chat[2])
        if chat[3] != superuserid:
            await bot.kick_chat_member(post[11], chat[3])

    db.deletepost(post[0])
    message_id = re.search(r'/(\d+)$', post[10]).group(1)
    await bot.delete_message(publicationbotid, message_id)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(userid, "Админ удалил один из ваших постов")


#superuser3
@dp.callback_query_handler(lambda call: call.data.startswith('calladminchat'))
async def admincall(call: types.CallbackQuery, state: FSMContext):
    encodeddata = call.data[13:]
    decoded_data = urllib.parse.parse_qs(encodeddata)

    chatid = decoded_data["chatid"][0]
    chat = db.chat_byid(call.message.chat.id)[0]
    post = db.findpost(chat[4])[0]
    invitelink = await bot.create_chat_invite_link(post[11], expire_date=99999999999999999)

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

    await bot.send_message(call.message.chat.id, "***Вы уверены, что вы хотите отменить сделку?***\n\nНапишите: `Да, я хочу отменить сделку`\n\nТекст можно скопировать, нажав на него\n***Важно*** После отмены чат будет удалён", parse_mode=types.ParseMode.MARKDOWN_V2)
    await CancelDeal.ackgnowledgment.set()


@dp.message_handler(state=CancelDeal.ackgnowledgment)
async def canceldealack(message: types.Message, state: FSMContext):
    if message.text == "Да, я хочу отменить сделку":
        chat = db.chat_byid(message.chat.id)[0]

        #chatdeletion
        db.clearpostchatid(chat[4])
        occupiedchats.remove(message.chat.id)
        chatbotids.append(message.chat.id)
        db.clear_chat(message.chat.id)

        await bot.delete_message(chat_id=chat[2], message_id=chat[6])
        await bot.delete_message(chat_id=chat[3], message_id=chat[5])

        await message.answer("Сделка отменена")
        await state.finish()
        await bot.unpin_all_chat_messages(message.chat.id)

        if chat[2] != superuserid:
            await bot.kick_chat_member(message.chat.id, chat[2])
        if chat[3] != superuserid:
            await bot.kick_chat_member(message.chat.id, chat[3])
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
@dp.message_handler(state=BecomeCompleter.phone)
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
            data["email"] = message.text

        await bot.send_message(message.from_user.id, "***Введите номер телефона***\n\nНажмите кнопку ***Поделится номером телефона***", reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN_V2)
        await BecomeCompleter.next()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)