# ===============================================================
# Author: Rodolfo Ferro Pérez
# Email: ferro@cimat.mx
# Twitter: @FerroRodolfo
#
# ABOUT COPYING OR USING PARTIAL INFORMATION:
# This script was originally created by Rodolfo Ferro. Any
# explicit usage of this script or its contents is granted
# according to the license provided and its conditions.
# ===============================================================
from flask import Flask, request
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from lang_dict import *
from geo_app import *
import logging

# You might need to add your tokens to this file...
from credentials import *


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# Global vars:
LANG = "EN"
SET_LANG, MENU, SET_STAT, REPORT, MAP, FAQ, ABOUT, LOCATION = range(8)
STATE = SET_LANG


def start(bot, update):
    """
    Start function. Displayed whenever the /start command is called.
    This function sets the language of the bot.
    """
    # Create buttons to slect language:
    keyboard = [['ES', 'EN']]

    # Create initial message:
    message = "Hey, I'm DisAtBot! / ¡Hey, soy DisAtBot! \n\n\
Please select a language to start. / Por favor selecciona un idioma \
para comenzar."

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text(message, reply_markup=reply_markup)

    return SET_LANG


def set_lang(bot, update):
    """
    First handler with received data to set language globally.
    """
    # Set language:
    global LANG
    LANG = update.message.text
    user = update.message.from_user

    logger.info("Language set by {} to {}.".format(user.first_name, LANG))
    update.message.reply_text(lang_selected[LANG],
                              reply_markup=ReplyKeyboardRemove())

    return MENU


def menu(bot, update):
    """
    Main menu function.
    This will display the options from the main menu.
    """
    # Create buttons to slect language:
    keyboard = [[Earn By PayPal Mining[LANG], Earn by Bitcoin Mining[LANG]],]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    user = update.message.from_user
    logger.info("Menu command requested by {}.".format(user.first_name))
    update.message.reply_text(main_menu[LANG], reply_markup=reply_markup)

    return SET_STAT


def set_state(bot, update):
    """
    Set option selected from menu.
    """
    # Set state:
    global STATE
    user = update.message.from_user
    if update.message.text == Earn By PayPal Mining[LANG]:
        STATE = REPORT
        payPal(bot, update)
        return MENU
    elif update.message.text == Earn by Bitcoin Mining[LANG]:
        STATE = MAP
        bitcoin(bot, update)
        return MENU
    else:
        STATE = MENU
        return MENU


def payPal(bot, update):
    """
    FAQ function. Displays FAQ about disaster situations.
    """
    user = update.message.from_user
    logger.info("Report requested by {}.".format(user.first_name))
    update.message.reply_text(loc_request[LANG])
    bot.send_message(chat_id=update.message.chat_id, text=back2menu[LANG])
    return 


def bitcoin(bot, update):
    """
    View map function. In development...
    """
    user = update.message.from_user
    logger.info("Report requested by {}.".format(user.first_name))
    update.message.reply_text(map_info[LANG])
    bot.send_message(chat_id=update.message.chat_id, text=back2menu[LANG])
    return 


def help(bot, update):
    """
    Help function.
    This displays a set of commands available for the bot.
    """
    user = update.message.from_user
    logger.info("User {} asked for help.".format(user.first_name))
    update.message.reply_text(help_info[LANG],
                              reply_markup=ReplyKeyboardRemove())


def cancel(bot, update):
    """
    User cancelation function.
    Cancel conersation by user.
    """
    user = update.message.from_user
    logger.info("User {} canceled the conversation.".format(user.first_name))
    update.message.reply_text(goodbye[LANG],
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

global bot
bot = telegram.Bot(token=telegram_token)

app = Flask(__name__)

@app.route('/{}'.format(telegram_token), methods=['POST'])
def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    global LANG
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SET_LANG: [RegexHandler('^(ES|EN)$', set_lang)],

            MENU: [CommandHandler('menu', menu)],

            SET_STAT: [RegexHandler(
                        '^({}|{}|{}|{})$'.format(
                            Earn By PayPal Mining['ES'], Earn by Bitcoin Mining['ES']),
                        set_state),
                       RegexHandler(
                        '^({}|{}|{}|{})$'.format(
                            Earn By PayPal Mining['EN'], Earn by Bitcoin Mining['EN']),
                        set_state)],

            # LOCATION: [MessageHandler(Filters.location, location),
            #            CommandHandler('menu', menu)]
        },

        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('help', help)]
    )

    dp.add_handler(conv_handler)

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    # updater.idle()
    # return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=telegram_token))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
    app.run(threaded=True)