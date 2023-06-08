import sqlite3

class DBclass:
    def __init__(self, database_file):

        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def makeuser(self, user_id, fullname):
        with self.connection:
            self.cursor.execute(
                'INSERT INTO `user` (`user_id`, `fullname`) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM `user` WHERE `user_id` = ?)',
                (user_id, fullname, user_id))

    def finduserbyid(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `user` WHERE `user_id` = ?;', (user_id,))
            return list(result)
    def publishpost(self, post):
        with self.connection:
            self.cursor.execute("INSERT INTO `post` (`user_id`, `active`, `completer`, `protection`, `theme`, `maintext`, `price`, `mediaid`, `docid`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (post.author, post.active, post.completer, post.protection, post.theme, post.maintext, post.price, post.mediaid, str(post.docid)))
            post_id = self.cursor.lastrowid
            return post_id
    def givepostalink(self, post_id, link):
        with self.connection:
            self.cursor.execute("UPDATE `post` SET `link` = ? WHERE `id` = ?;", (link, post_id,))

    def findallposts(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `post` WHERE `user_id` = ?;', (user_id,))
            return list(result)
    def deletepost(self, id):
        with self.connection:
            return self.cursor.execute('DELETE FROM `post` WHERE `id` = ?;', (id,))
    def findpost(self, id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `post` WHERE `id` = ?;', (id,))
            return list(result)

    def createchat(self, chat_id):
        with self.connection:
            self.cursor.execute('INSERT INTO `chats` (`chat_id`) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM `chats` WHERE `chat_id` = ?)', (chat_id, chat_id,))
    def update_chat(self, chat_id, completer_id, user_id, post_id):
        with self.connection:
            self.cursor.execute("UPDATE chats SET completer_id = ?, user_id = ?, post_id = ? WHERE chat_id = ?;", (completer_id, user_id, post_id, chat_id,))
    def update_chat_links(self, chat_id, userinvite, completerinvite):
        with self.connection:
            self.cursor.execute("UPDATE chats SET userinvite = ?, completerinvite = ? WHERE chat_id = ?;", (userinvite, completerinvite, chat_id,))
    def find_chat_byid(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `chats` WHERE `completer_id` = ? OR `user_id` = ?;', (user_id, user_id,))
            return list(result)
    def chat_byid(self, chatid):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_id` = ?;", (chatid,))
            return list(result)
    def postidchat(self, postid):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `chats` WHERE `post_id` = ?;", (postid,))
            return list(result)
    def clear_chat(self, chat_id):
        with self.connection:
            self.cursor.execute("UPDATE chats SET completer_id = NULL, user_id = NULL, post_id = NULL, userinvite = NULL, completerinvite = NULL WHERE chat_id = ?;", (chat_id,))
    def clearpostchatid(self, id):
        with self.connection:
            self.cursor.execute("UPDATE post SET `chat` = NULL WHERE `id` = ?;", (id,))

    def getchatdetails(self, chat_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `chats` WHERE `chat_id` = ?;', (chat_id,))
            return list(result)
    def getalloccupiedchats(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `chats` WHERE `post_id` IS NOT NULL;')
            return list(result)
    def add_chat_to_post(self, postid, chatid):
        with self.connection:
            self.cursor.execute('UPDATE `post` SET `chat` = ? WHERE `id` = ?', (chatid, postid,))
    def createcompleter(self, completer_id, name, email, date, phone, isactive, bal):
        with self.connection:
            self.cursor.execute("INSERT INTO `completer` (`completer_id`, `name`, `email`, `date`, `phone`, `isactive`, `balance`) VALUES (?, ?, ?, ?, ?, ?, ?)", (completer_id, name, email, date, phone, isactive, bal))
    def getcompleter(self, completer_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `completer` WHERE `completer_id` = ?;', (completer_id,))
            return list(result)
    def updatecompleterstatus(self, completer_id, isactive):
        with self.connection:
            self.cursor.execute("UPDATE `completer` SET `isactive` = ? WHERE `completer_id` = ?", (isactive, completer_id,))
class Post():
    def __init__(self, active, author, completer, protection, theme, maintext, price, mediaid, docid):
        # clientside ---
        self.active = active
        self.author = author
        self.completer = completer
        self.protection = protection
        # --------------
        self.theme = theme
        self.maintext = maintext
        self.price = price
        self.mediaid = mediaid
        self.docid = docid
    def tostring(self):

        return f"{'🔵 ' + self.active if self.protection == 'protected' else '🔴 ' + self.active} \n\n<b>{self.theme}</b> \n\n{self.maintext} \n\nЦена: {self.price if self.price == 'Договорная' else self.price + ' грн'}\n{'<b>Защищённый пост</b>' if self.protection == 'protected' else ''}\n {self.mediaid if self.mediaid else ''} {self.docid[0] if self.docid else ''}"