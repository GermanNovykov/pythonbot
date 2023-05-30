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
            self.cursor.execute("INSERT INTO `post` (`user_id`, `active`, `completer`, `protection`, `theme`, `maintext`, `price`, `mediaid`, `docid`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (post.author, post.active, post.completer, post.protection, post.theme, post.maintext, post.price, post.mediaid, post.docid))
            post_id = self.cursor.lastrowid
            return post_id
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
        return f"🔵{self.active} \n\n<b>{self.theme}</b> \n\n{self.maintext} \n\nЦена: {self.price if self.price == 'Договорная' else self.price + ' грн'} \n {self.mediaid if self.mediaid else self.docid}"