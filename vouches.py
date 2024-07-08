import telebot
from telebot import types


def handle_callback_query(call):
    if call.data == "vouches":
        # Create an inline keyboard for vouches options
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("Your Vouches", callback_data="your_vouches"),
            types.InlineKeyboardButton("Search for Vouches", callback_data="search_vouches")
        )
        keyboard.row(
            types.InlineKeyboardButton("Submit a Vouch", callback_data="submit_vouch"),
            types.InlineKeyboardButton("Back to Main", callback_data="main_options")
        )

        bot.send_message(call.message.chat.id, "Vouches Options:", reply_markup=keyboard)
    elif call.data == "your_vouches":
        # Handle action for "Your Vouches"
        bot.send_message(call.message.chat.id, "You selected Your Vouches.")
    elif call.data == "search_vouches":
        # Handle action for "Search for Vouches"
        bot.send_message(call.message.chat.id, "You selected Search for Vouches.")
    elif call.data == "submit_vouch":
        # Handle action for "Submit a Vouch"
        bot.send_message(call.message.chat.id, "You selected Submit a Vouch.")
    elif call.data == "main_options":
        # Handle action for "Back to Main"
        # Create an inline keyboard for main options
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

        bot.send_message(call.message.chat.id, "Please choose an option:", reply_markup=keyboard)