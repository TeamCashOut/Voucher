import telebot
import sqlite3

class UserProfile:
    def __init__(self, user_id, username, vouches=0, complaints=0, vouch_description="", joined_date="",
                 telegram_alt_account="", forum_profiles="", associated_communities=""):
        self.user_id = user_id
        self.username = username
        self.vouches = vouches
        self.complaints = complaints
        self.vouch_description = vouch_description
        self.joined_date = joined_date
        self.telegram_alt_account = telegram_alt_account
        self.forum_profiles = forum_profiles
        self.associated_communities = associated_communities

class UserDatabase:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.c = self.conn.cursor()
        self.init_tables()
        self.conn.commit()

    def init_tables(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                vouches INTEGER DEFAULT 0,
                complaints INTEGER DEFAULT 0,
                vouch_description TEXT,
                joined_date TEXT,
                telegram_alt_account TEXT,
                forum_profiles TEXT,
                associated_communities TEXT
            )
        ''')

    def add_user(self, user_id, username, joined_date):
        with self.conn:
            self.c.execute("INSERT INTO users (user_id, username, joined_date) VALUES (?, ?, ?)",
                        (user_id, username, joined_date))

    def get_user(self, user_id):
        self.c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = self.c.fetchone()
        if result:
            return UserProfile(*result)
        return None

    def update_vouches(self, user_id, vouches):
        with self.conn:
            self.c.execute("UPDATE users SET vouches = ? WHERE user_id = ?", (vouches, user_id))

    def update_complaints(self, user_id, complaints):
        with self.conn:
            self.c.execute("UPDATE users SET complaints = ? WHERE user_id = ?", (complaints, user_id))

    def update_vouch_description(self, user_id, vouch_description):
        with self.conn:
            self.c.execute("UPDATE users SET vouch_description = ? WHERE user_id = ?", (vouch_description, user_id))

    def update_telegram_alt_account(self, user_id, telegram_alt_account):
        with self.conn:
            self.c.execute("UPDATE users SET telegram_alt_account = ? WHERE user_id = ?", (telegram_alt_account, user_id))

    def update_forum_profiles(self, user_id, forum_profiles):
        with self.conn:
            self.c.execute("UPDATE users SET forum_profiles = ? WHERE user_id = ?", (forum_profiles, user_id))

    def update_associated_communities(self, user_id, associated_communities):
        with self.conn:
            self.c.execute("UPDATE users SET associated_communities = ? WHERE user_id = ?", (associated_communities, user_id))

bot_token = '<YOUR_BOT_TOKEN>'
db = UserDatabase('user_profiles.db')
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    user = db.get_user(user_id)
    if user:
        vouches = user.vouches
        complaints = user.complaints
        joined_date = user.joined_date
        telegram_alt_account = user.telegram_alt_account
        forum_profiles = user.forum_profiles
        associated_communities = user.associated_communities

        profile_message = f"👤 User ID: {user_id}\n" \
                          f"🌐 Username: @{username}\n" \
                          f"✅ Vouches: {vouches}\n" \
                          f"❌ Complaints: {complaints}\n" \
                          f"📅 Joined Date: {joined_date}\n" \
                          f"🙋‍♂️ Telegram Alt Account: {telegram_alt_account}\n" \
                          f"💬 Forum Profiles:\n{forum_profiles}\n" \
                          f"🌍 Associated Communities:\n{associated_communities}"
        bot.reply_to(message, profile_message)
    else:
        bot.reply_to(message, "User profile not found.")

@bot.message_handler(commands=['update_vouches'])
def handle_update_vouches(message):
    user_id = message.from_user.id
    vouches = int(message.text.split()[1])

    db.update_vouches(user_id, vouches)
    bot.reply_to(message, f"Vouches updated: {vouches}")

@bot.message_handler(commands=['update_complaints'])
def handle_update_complaints(message):
    user_id = message.from_user.id
    complaints = int(message.text.split()[1])

    db.update_complaints(user_id, complaints)
    bot.reply_to(message, f"Complaints updated: {complaints}")

@bot.message_handler(commands=['update_alt_account'])
def handle_update_alt_account(message):
    user_id = message.from_user.id
    telegram_alt_account = message.text.split()[1]

    db.update_telegram_alt_account(user_id, telegram_alt_account)
    bot.reply_to(message, f"Telegram Alt Account updated: {telegram_alt_account}")

@bot.message_handler(commands=['update_forum_profiles'])
def handle_update_forum_profiles(message):
    user_id = message.from_user.id
    forum_profiles = message.text.split()[1]

    db.update_forum_profiles(user_id, forum_profiles)
    bot.reply_to(message, f"Forum Profiles updated:\n{forum_profiles}")

@bot.message_handler(commands=['update_assoc_communities'])
def handle_update_assoc_communities(message):
    user_id = message.from_user.id
    associated_communities = message.text.split()[1]

    db.update_associated_communities(user_id, associated_communities)
    bot.reply_to(message, f"Associated Communities updated:\n{associated_communities}")
