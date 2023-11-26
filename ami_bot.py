import telebot
from Core.User import User
from telebot import types
from Core.AmizoneFetcher import AmizoneFetcher
from  datetime import date

TOKEN = '6507971785:AAFuZRJjwkDlmQLaynPJLY3kJkCR6QGKvhI'
user = User()
bot = telebot.TeleBot(TOKEN)

user_states = {}
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/time for timetable\n/attendance for attendance\n/login to update login credentials\nEnjoy Your session)")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "To start, please /login.")

@bot.message_handler(commands=['login'])
def login(message):
    bot.send_message(message.chat.id, "Please enter your username:")
    bot.register_next_step_handler(message, process_username_step)

def process_username_step(message):
    user.set_login(message.text)

    bot.send_message(message.chat.id, "Please enter your password:")
    bot.register_next_step_handler(message, process_password_step)

def process_password_step(message):
    bot.send_message(message.chat.id, "Wait, please ⏳")
    user.set_password(message.text)

    user_login, password = user.get_credentials()
    ami_fetcher = AmizoneFetcher()
    ami_fetcher.setCredentials(user_login, password)

    if ami_fetcher.login():
        bot.send_message(message.chat.id, "Login successful!")
        user_states[message.chat.id] = {'logged_in': True}
        help(message)
    else:
        bot.send_message(message.chat.id, "Incorrect credentials. Login failed.")
    ami_fetcher.dispose()

@bot.message_handler(commands=['time'])
def time(message):

    user_state = user_states.get(message.chat.id, {})
    if user_state.get('logged_in', False):

        #if date.today().weekday() == 5 or date.today().weekday() == 6:
         #   bot.send_message(message.chat.id, "No time table on weekend")
          #  return
        
        user_login, password = user.get_credentials()
        ami_fetcher = AmizoneFetcher()
        ami_fetcher.setCredentials(user_login, password)

        msg = ""
        time_table = ami_fetcher.fetch_time_table()
        
        for i in time_table:
            subject, color = i
            if(color == "red"):
                color = "🔴"
            elif(color == "green"):
                color = "🟢"
            else:
                color = "🔵"
            msg += subject + "  " + color + "\n"
        bot.send_message(message.chat.id, msg)
        ami_fetcher.dispose()
    else:
        bot.send_message(message.chat.id, "First you need to /login")


@bot.message_handler(commands=['attendance'])
def attendance(message):
    user_state = user_states.get(message.chat.id, {})
    
    if user_state.get('logged_in', False):
        msg = ""
        user_login, password = user.get_credentials()
        ami_fetcher = AmizoneFetcher()
        ami_fetcher.setCredentials(user_login, password)

        #Don't now for sure color range of attendence, thats why I use my own: 0-74.9 -> red, 75-84.9 -> yellow, 85-100 -> green
        statistics = ami_fetcher.compute_overall_statistics()

        for subject in statistics:
            attended_lessons, all_lessons = statistics[subject]
            percentage = round(attended_lessons/ all_lessons,2) * 100
            if percentage > 0 and percentage < 75:
                emoji = "🟥"
            elif percentage >= 75 and percentage < 85:
                emoji = "🟨"
            else:
                emoji = "🟩"
            msg += subject + " : " + str(attended_lessons) + "/" + str(all_lessons) + " -> " + str(percentage) + "%  " + emoji + "\n"
        

        bot.send_message(message.chat.id, msg)
        ami_fetcher.dispose()
    else:
        bot.send_message(message.chat.id, "First you need to /login")

bot.polling()