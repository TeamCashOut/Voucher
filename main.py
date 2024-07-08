import telebot
import sqlite3
import threading
from telebot import types
import admin_menu
import admin_adverts
import promotion_groups
import user_complaints
import user_menu
import user_vouches
import vouches
import user_profile

conn = sqlite3.connect('vouches_complaints.db', check_same_thread=False)
c = conn.cursor()

db_lock = threading.Lock()
conn.commit()

# Create necessary tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        vouches INTEGER DEFAULT 0,
        complaints INTEGER DEFAULT 0,
        vouch_description TEXT,
        joined_date TEXT,
        forum_profiles TEXT,
        associated_communities TEXT,
        telegram_alt_account TEXT
    )
''')
conn.commit()

c.execute('''
    CREATE TABLE IF NOT EXISTS vouches (
        vouch_id INTEGER PRIMARY KEY,
        vouched_by INTEGER,
        vouched_user INTEGER,
        vouch_description TEXT,
        anonymous INTEGER DEFAULT 0,
        FOREIGN KEY (vouched_by) REFERENCES users (user_id),
        FOREIGN KEY (vouched_user) REFERENCES users (user_id)
    )
''')
conn.commit()

c.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id INTEGER PRIMARY KEY,
        complainant INTEGER,
        complained_user INTEGER,
        FOREIGN KEY (complainant) REFERENCES users (user_id),
        FOREIGN KEY (complained_user) REFERENCES users (user_id)
    )
''')
conn.commit()



bot_token = '7325738660:AAHqCKq-UEkTbPM1zAZrQg-gelAlaBaK7vs'

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['RYR', 'start'])
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    vouches = 0
    complaints = 0
    profile_message = ""
    
    with db_lock:
        c.execute("SELECT vouches, complaints, telegram_alt_account, forum_profiles FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
    
        if result is not None:
            vouches = result[0]
            complaints = result[1]
            telegram_alt_account = result[2]
            forum_profiles = result[3]
            associated_communities = result[4]
    
            profile_message = f"👤 User ID: {user_id}\n" \
                            f"👥 Telegram Alt Account: {telegram_alt_account}\n" \
                            f"🌐 Forum Profiles: {forum_profiles}\n" \
                            f"🌍 Associated TG Communities: {associated_communities}"
    
    stats_message = f"📊 Your Stats:\n\n✅ Vouches: {vouches}\n❌ Complaints: {complaints}\n\n{profile_message}"
    
    welcome_message = f"👋 Welcome, {username}!\n\n{stats_message}"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Vouches", callback_data="vouches"),
        types.InlineKeyboardButton("Complaints", callback_data="complaints")
    )
    keyboard.row(
        types.InlineKeyboardButton("Check", callback_data="check"),
        types.InlineKeyboardButton("Profile", callback_data="profile")
    )
    keyboard.row(
        types.InlineKeyboardButton("Support", callback_data="support")
    )
    
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard)
    

@bot.message_handler(commands=['admin'])
def admin(message):
    admin_menu = admin_menu.build_admin_menu()
    
    bot.send_message(message.chat.id, "Admin Menu", reply_markup=admin_menu)



@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == "vouches":
        bot.send_message(call.message.chat.id, "You selected Vouches.")
        user_vouches.show_vouches(call.message)
    elif call.data == "complaints":
        bot.send_message(call.message.chat.id, "You selected Complaints.")
        user_complaints.show_complaints(call.message)
    elif call.data == "check":
        bot.send_message(call.message.chat.id, "You selected Check.")
        user_menu.show_check(call.message)  
    elif call.data == "profile":
        user_id = call.from_user.id
        username = call.from_user.username
        
        with db_lock:
            c.execute("SELECT vouches, complaints, joined_date, telegram_alt_account, forum_profiles, users WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            
            if result is not None:
                vouches = result[0]
                complaints = result[1]
                joined_date = result[2]
                telegram_alt_account = result[3] or "N/A"
                forum_profiles = result[4] or "N/A"
                
                profile_message = f"Username: @{username}\n" \
                                  f"User ID: {user_id}\n\n" \
                                  f"Vouches: {vouches}\n" \
                                  f"Complaints: {complaints}\n\n" \
                                  f"User Joined Date: {joined_date}\n\n" \
                                  f"Forum Profiles: \n{forum_profiles}"
                
                keyboard = types.InlineKeyboardMarkup()
                keyboard.row(
                    types.InlineKeyboardButton("Edit Telegram Alt Account", callback_data="edit_telegram_alt"),
                    types.InlineKeyboardButton("Edit Forum Profiles", callback_data="edit_forum_profiles")
                )
                keyboard.row(
                    types.InlineKeyboardButton("Edit Associated Groups", callback_data="edit_associated_groups")
                )
                
                bot.send_message(call.message.chat.id, f"Your Profile:\n\n{profile_message}", reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, "No profile available.")
    
    elif call.data == "support":
        bot.send_message(call.message.chat.id, "You selected Support.")
    
    elif call.data == "add_telegram_alt":
        bot.send_message(call.message.chat.id, "You selected Add Telegram Alt Account.")
    elif call.data == "add_forum_profiles":
        bot.send_message(call.message.chat.id, "You selected Add Associated Forum Profiles.")
    elif call.data == "add_tg_groups":
        bot.send_message(call.message.chat.id, "You selected Add Associated TG Groups.")

@bot.message_handler(commands=['vouch'])
def handle_vouch(message):
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a message to vouch for a user.")
        return
    
    replied_message = message.reply_to_message
    if not replied_message.from_user:
        bot.reply_to(message, "The replied message does not have a valid user.")
        return
    
    vouched_user_id = replied_message.from_user.id
    vouched_user_username = replied_message.from_user.username
    vouch_by_user_id = message.from_user.id
    vouch_by_user_username = message.from_user.username
    
    with db_lock:
        c.execute("SELECT COUNT(*) FROM vouches WHERE vouched_by=? AND vouched_user=?", (vouch_by_user_id, vouched_user_id))
        result = c.fetchone()
        
        if result[0] == 0:
            c.execute("INSERT INTO vouches (vouched_by, vouched_user) VALUES (?, ?)",
                      (vouch_by_user_id, vouched_user_id))
            conn.commit()
            
            confirmation_message = f"You are submitting a vouch for {vouched_user_username}\n\n" \
                                   f"User Information:\n" \
                                   f"Username: @{vouched_user_username}\n" \
                                   f"User ID: {vouched_user_id}\n\n" \
                                   f"If you want to proceed, please reply with a 20-word max vouch description."
            
            bot.send_message(vouch_by_user_id, confirmation_message)
        else:
            bot.reply_to(message, "You have already recently submitted a voucher for this user.\nPlease allow at least a 30-minute timer")
            
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_vouch_description(message):
    vouch_by_user_id = message.from_user.id
    description = message.text.strip()
    if len(description.split()) > 20:
        bot.send_message(vouch_by_user_id, "Please limit the vouch description to a maximum of 20 words.")
    else:
        with db_lock:
            c.execute("UPDATE vouches SET vouch_description=? WHERE vouched_by=?", (description, vouch_by_user_id))
            conn.commit()
        anonymous_message = "Would you like to remain anonymous in the vouch?\n" \
                            "Please reply with 'Yes' or 'No'."
        bot.send_message(vouch_by_user_id, anonymous_message)

@bot.message_handler(func=lambda message: message.text.lower() in ['yes', 'no'], content_types=['text'])
def handle_anonymous_preference(message):
    vouch_by_user_id = message.from_user.id
    anonymous_preference = message.text.lower() == 'yes'
    with db_lock:
        c.execute("UPDATE vouches SET anonymous=? WHERE vouched_by=?", (anonymous_preference, vouch_by_user_id))
        conn.commit()
    if anonymous_preference:
        bot.send_message(vouch_by_user_id, "Thank you for your vouch submission. Your vouch will remain anonymous.")
    else:
        bot.send_message(vouch_by_user_id, "Thank you for your vouch submission. Your vouch will not remain anonymous.")

@bot.message_handler(commands=['complain'])
def handle_complain(message):
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a message to complain about a user.")
        return
    
    replied_message = message.reply_to_message
    if not replied_message.from_user:
        bot.reply_to(message, "The replied message does not have a valid user.")
        return
    
    complained_user_id = replied_message.from_user.id
    complained_user_username = replied_message.from_user.username
    complainant_user_id = message.from_user.id
    complainant_user_username = message.from_user.username
    
    with db_lock:
        c.execute("SELECT COUNT(*) FROM complaints WHERE complainant=? AND complained_user=?", (complainant_user_id, complained_user_id))
        result = c.fetchone()
        
        if result[0] == 0:
            c.execute("INSERT INTO complaints (complainant, complained_user) VALUES (?, ?)",
                      (complainant_user_id, complained_user_id))
            conn.commit()
            
            c.execute("UPDATE users SET complaints = complaints + 1 WHERE user_id=?", (complained_user_id,))
            conn.commit()
            
            bot.reply_to(
                message, f"You have complained about {complained_user_username}")
        else:
            bot.reply_to(message, "You have already complained about this user.")

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a message to view the stats.")
        return
    
    replied_message = message.reply_to_message
    if not replied_message.from_user:
        bot.reply_to(message, "The replied message does not have a valid user.")
        return
    
    username = replied_message.from_user.username
    
    with db_lock:
        c.execute("SELECT vouches, complaints, telegram_alt_account, forum_profiles, associated_communities FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        
        if result is not None:
            vouches = result[0]
            complaints = result[1]
            telegram_alt_account = result[2]
            forum_profiles = result[3]
            associated_communities = result[4]
            
            profile_message = f"👤 User ID: {replied_message.from_user.id}\n" \
                              f"🌐 Username: @{username}\n" \
                              f"👥 Telegram Alt Account: {telegram_alt_account}\n" \
                              f"🌐 Forum Profiles: {forum_profiles}\n" \
                              f"🌍 Associated TG Communities: {associated_communities}"
            stats_message = f"📊 Stats for {username}:\n\n✅ Vouches: {vouches}\n❌ Complaints: {complaints}\n\n{profile_message}"
        else:
            stats_message = f"📊 No stats available for {username}.\n\n{profile_message}"
        
        bot.reply_to(message, stats_message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def handle_edit_menu(call):
    user_id = call.from_user.id
    
    if call.data == "edit_telegram_alt":
        bot.send_message(user_id, "You selected Edit Telegram Alt Account.")
    elif call.data == "edit_forum_profiles":
        bot.send_message(user_id, "You selected Edit Forum Profiles.")
    elif call.data == "edit_associated_groups":
        bot.send_message(user_id, "You selected Edit Associated Groups.")

if __name__ == "__main__":
    bot.polling()