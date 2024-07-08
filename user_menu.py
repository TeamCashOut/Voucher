import telebot
from telebot import types
from main import bot


def show_menu(chat_id):
  bot.send_message(chat_id, "Main Menu")

def main_menu_keyboard(message):

  # Create inline keyboard
  keyboard = types.InlineKeyboardMarkup()   
  
  # Add main menu options
  key_vouches = types.InlineKeyboardButton(text='Vouches', callback_data='vouches')
  keyboard.add(key_vouches)

  # Other options...
  
  # Send inline keyboard
  bot.send_message(message.chat.id, "Select an option:", reply_markup=keyboard)




def show_check(message):
    pass