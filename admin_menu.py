from telebot import types 
from main import bot 

def build_admin_menu():
    admin_keyboard = types.InlineKeyboardMarkup()
    
    admin_keyboard.row(
        types.InlineKeyboardButton("Ban User", callback_data="ban"),
        types.InlineKeyboardButton("Warn User", callback_data="warn")
    )
    admin_keyboard.row(
        types.InlineKeyboardButton("Promote User", callback_data="promote"),
        types.InlineKeyboardButton("Demote User", callback_data="demote")
    )
    admin_keyboard.row(
        types.InlineKeyboardButton("Review Reports", callback_data="reports"),
        types.InlineKeyboardButton("Broadcast", callback_data="broadcast")
    )
    admin_keyboard.row(
        types.InlineKeyboardButton("Admin Stats", callback_data="stats")
    )
    return admin_keyboard
    



@bot.callback_query_handler(func=lambda call: call.data == 'ban')
def ban(call):
    user_id = call.message.reply_to_message.from_user.id
    bot.kick_chat_member(call.message.chat.id, user_id)
    bot.send_message(call.message.chat.id, 
        f"👤 User {user_id} has been banned from the group") 
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'warn')
def warn(call):

    user_id = call.message.reply_to_message.from_user.id
    username = call.from_user.username
    reason = call.message.text.split('/warn')[1].strip() 
    warning_message = f"⚠️ User {user_id} has been warned"
    
    if reason:
        warning_message += f"\nWarning Reason: {reason}"
    bot.send_message(call.message.chat.id, warning_message)
    try:
        bot.send_message(user_id, "You have received a warning in the group chat.") 
    except Exception as e:
        print(f"Error sending PM to {user_id}: {e}")
    max_warnings = 3
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        
        current_warnings = c.execute("SELECT warnings FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
        
        if current_warnings >= max_warnings:
            bot.kick_chat_member(call.message.chat.id, user_id)
            bot.send_message(call.message.chat.id, f"{user_id} reached max warnings and has been banned.")
        else:
            c.execute("UPDATE users SET warnings = warnings + 1 WHERE user_id = ?", (user_id,))
    bot.answer_callback_query(call.id, "User has been warned!")

@bot.callback_query_handler(func=lambda call: call.data == 'promote')
def promote(call):
    user_id = call.message.reply_to_message.from_user.id
    bot.promote_chat_member(call.message.chat.id, user_id, can_change_info=True, can_post_messages=True, can_edit_messages=True, can_delete_messages=True, can_invite_users=True, can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
    bot.answer_callback_query(call.id, "User promoted!")


@bot.callback_query_handler(func=lambda call: call.data == 'demote')
def demote(call):
    user_id = call.message.reply_to_message.from_user.id
    bot.restrict_chat_member(call.message.chat.id, user_id, can_change_info=False, can_post_messages=False, can_edit_messages=False, can_delete_messages=False, can_invite_users=False, can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
    bot.answer_callback_query(call.id, "User demoted!")


@bot.callback_query_handler(func=lambda call: call.data == 'reports')
def reports(call):
    bot.send_message(call.message.chat.id, "Here are the latest user reports:")
    with sqlite3.connect('reports.db') as conn:
        c = conn.cursor()
        for row in c.execute("SELECT * FROM reports ORDER BY date DESC LIMIT 10"):
            reported_msg = row[0]
            report_reason = row[1]
            bot.forward_message(call.message.chat.id, reported_msg.chat.id, reported_msg.message_id)
            bot.send_message(call.message.chat.id, f"Report reason: {report_reason}")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast')
def broadcast(call):
    message = call.message.text.split('/broadcast')[1].strip()
    if not message:
        bot.answer_callback_query(call.id, "No message provided to broadcast!")
        return
    bot.send_message(call.message.chat.id, "Broadcasting message...")
    # Send message to all users
    for user in get_all_users():
        try:
            bot.send_message(user.id, message)
        except Exception as e:
            print(f"Failed to send to {user}: {e}")
    bot.answer_callback_query(call.id, "Broadcast complete!")


@bot.callback_query_handler(func=lambda call: call.data == 'stats')  
def stats(call):
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    message_count = db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    stats_msg = f"📊 <b>Admin Stats</b>\n\n➡️ Total Users: {user_count}\n➡️ Total Messages: {message_count}"
    bot.send_message(call.message.chat.id, stats_msg, parse_mode='HTML')
    bot.answer_callback_query(call.id)

# Send admin menu
@bot.message_handler(commands=['admin'])
def admin(message):
    admin_menu = build_admin_menu()
    bot.send_message(message.chat.id, "Admin Menu", reply_markup=admin_menu)