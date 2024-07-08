import telebot
from telebot import types
import user_menu
import telebot

ADMIN_ID = None # To be set by main.py
bot = None # To be set by main.py
vouches_pending = []

def vouches_menu(message):
    # Send explanation message
    bot.send_message(message.chat.id, "Use this menu to manage vouchers. You can send and check vouchers, or view your voucher balance.")
    keyboard = types.InlineKeyboardMarkup()
    key_send = types.InlineKeyboardButton(text='Send Voucher', callback_data='send_voucher')
    keyboard.add(key_send)
    key_check = types.InlineKeyboardButton(text='Check Voucher', callback_data='check_voucher')
    keyboard.add(key_check)
    key_myvouches = types.InlineKeyboardButton(text='My Vouchers', callback_data='my_vouchers')
    keyboard.add(key_myvouches)
    key_mainmenu = types.InlineKeyboardButton(text='Main Menu', callback_data='main_menu')
    keyboard.add(key_mainmenu)

    bot.send_message(message.chat.id, "Select an option:", reply_markup=keyboard)


def send_voucher(message):
  bot.send_message(message.chat.id, "Enter voucher amount and recipient's username:")





def confirm_vouch(message, service, cost, date, rating):

  # Confirmation keyboard
  
  @bot.callback_query_handler(func=lambda call: call.data == "confirm")
  def confirm(call):
    # Send for approval
    vouch_details = f"Service: {service}, Cost: {cost}..." 
    send_for_approval(vouch_details)
    
    bot.send_message(call.message.chat.id, "Vouch pending approval!")






def approve_vouch(message):

  if message.from_user.id != ADMIN_ID:
    return

  if not vouches_pending:
    bot.send_message(message.chat.id, "No pending vouches!")
    return

  vouch = vouches_pending.pop(0)  
  user_id = vouch['user_id']
  service = vouch['service']
  cost = vouch['cost']
  date = vouch['date']
  rating = vouch['rating']
  save_vouch_to_db(user_id, service, cost, date, rating)
  bot.send_message(message.chat.id, "Vouch approved and saved!")
  bot.send_message(user_id, "Your vouch has been approved!")

def send_for_approval(vouch_details, user_id, vouched_user_id):

  # Get user profiles
  user = get_user_profile(user_id)
  vouched_user = get_user_profile(vouched_user_id)

  message = f"New vouch pending approval:\n\n"

  # User stats
  message += f"From: @{user.username}\n"
  message += f"Reputation: {user.reputation_score}\n"
  message += f"Vouches: {user.vouches_given_count}\n\n"

  # Vouched user stats
  message += f"For: @{vouched_user.username}\n" 
  message += f"Reputation: {vouched_user.reputation_score}\n"
  message += f"Vouches: {vouched_user.vouches_received_count}\n\n"

  # Vouch details
  message += f"Vouch Details: {vouch_details}"

  bot.send_message(ADMIN_ID, message)

def confirm_vouch(message, service, cost, date, rating, vouched_user_id):

  # Package vouch details
  vouch_details = f"Service: {service}\n"
  vouch_details += f"Cost: {cost}\n"
  vouch_details += f"Date: {date}\n" 
  vouch_details += f"Rating: {rating} stars"

  # Call approval function
  send_for_approval(
    vouch_details, 
    message.from_user.id, 
    vouched_user_id
  )

  bot.send_message(message.chat.id, "Vouch pending approval!")


  
def confirm(call):
  confirm_vouch(
    call.message, 
    service, 
    cost,
    date,
    rating,
    vouched_user_id
  )



def check_voucher(message):
  bot.send_message(message.chat.id, "Enter voucher code:")

  @bot.message_handler(func=lambda m: True)
  def check_voucher_handler(message):
    voucher_code = message.text

    # Lookup voucher code in database
    voucher = get_voucher_from_db(voucher_code)

    if voucher:
      # Voucher found
      bot.send_message(message.chat.id, f"Voucher found! Amount: {voucher['amount']}, Recipient: {voucher['recipient']}")
    else:
      # Voucher not found
      bot.send_message(message.chat.id, "Invalid voucher code!")







def my_vouchers(message):
  # Lookup vouchers for user in database
  vouchers = get_user_vouchers(message.from_user.id)
  if vouchers:

    bot.send_message(message.chat.id, format_vouchers(vouchers)) 
  else:
    bot.send_message(message.chat.id, "You have no vouchers!")




def main_menu(message):
  bot.delete_message(message.chat.id, message.message_id)  
  user_menu.show_menu(message.chat.id)
  user_menu.main_menu_keyboard(message)
    
    
    
    
    
    
def callback_query(call):
    if call.data == "send_voucher":
        send_voucher(call.message)
    elif call.data == "check_voucher":
        check_voucher(call.message)
    elif call.data == "my_vouchers":
        my_vouchers(call.message)
    elif call.data == "main_menu":
        main_menu(call.message)