from time import thread_time_ns
import telebot
import os
from dotenv import load_dotenv
import json
from telebot import types
import busArrival
import shelve

load_dotenv('variables.env')
API_KEY = os.getenv('DATAMALL_API_KEY')
my_bot_token = os.getenv('BOT_TOKEN')

user_data = {} # temp storage before appending to the shelve
# busDB = {
#     user_id: {
#         bus_stop_code_1: [bus1, bus2],
#         bus_stop_code_2: [bus3, bus4],
#     }
# }

if (my_bot_token == None):
    print("No BOT_TOKEN found")
    raise ValueError("No bot token found")
if (API_KEY == None):
    print("No API KEY detected")
    raise ValueError("No API Key found")

bot = telebot.TeleBot(my_bot_token)
def main():
    print("Bot is running...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['add'])
def add_bus_to_dictionary(message):
    markup = types.ForceReply(selective=False)
    sent = bot.send_message(message.chat.id, "Please enter bus stop code: ", reply_markup=markup)
    bot.register_next_step_handler(sent, process_buscode)

def process_buscode(reply):
    print(reply.text)

    user_id = str(reply.from_user.id)
    busStopCode = reply.text.strip()
    
    user_data[user_id] = {'busStopCode': busStopCode} # this is the .put() function

    markup = types.ForceReply(selective=False)
    sent = bot.send_message(reply.chat.id, "Enter bus numbers to track: 21 131 145", reply_markup=markup)
    bot.register_next_step_handler(sent, process_buslist)

def process_buslist(reply):
    user_id = str(reply.from_user.id) 
    # deals with concurrent users
    if user_id not in user_data:
        bot.send_message(reply.chat.id, "Session expired, try again")
    
    bus_list = reply.text.strip()
    busServiceNumbers = bus_list.split()
    bus_stop_code = user_data[user_id]['busStopCode']

    # user_data[user_id] = {'busServiceNumbers': busServiceNumbers}
    with shelve.open('busDB', writeback=True) as db:
        if user_id not in db:
            db[user_id] = {}
        
        if bus_stop_code not in db[user_id]:
            db[user_id][bus_stop_code] = []

        for bus in busServiceNumbers:
            if bus not in db[user_id][bus_stop_code]:
                db[user_id][bus_stop_code].append(bus)

    bot.send_message(reply.chat.id, f"Tracking {bus_list} at {bus_stop_code}")
    del user_data[user_id]


@bot.message_handler(commands=['bus'])
def send_bus_timing(message):
    user_id = str(message.from_user.id)
    with shelve.open('busDB') as db:
        # print(db[chat_id])
        # bot.send_message(message.chat.id, f"Tracking: {db[chat_id]}")
        user_data = db[user_id]
        for bus_stop in user_data.keys():
            message_for_bus_stop = f"Bus Stop Code: {bus_stop}\n\n"
            print(bus_stop)
            response = busArrival.getBusArrivalResponse(bus_stop, None, API_KEY)
            for bus_service_no in user_data[bus_stop]:
                print(bus_service_no)
                busTimingString = busArrival.getBusTiming(response, bus_stop, bus_service_no)
                print(f"message = {busTimingString}")
                # bot.send_message(message.chat.id, busTimingString)
                message_for_bus_stop += busTimingString
                message_for_bus_stop += "\n"

            if message_for_bus_stop == "":
                message_for_bus_stop = f"No bus information available for this bus"
            bot.send_message(message.chat.id, message_for_bus_stop)

@bot.message_handler(commands=['list'])
def list_bus_stops(message):
    user_id = str(message.from_user.id)
    
    reply = ""

    with shelve.open('busDB') as db:
        print(db[user_id])

        user_data = db[user_id]
        for bus_stop in user_data.keys():
            reply += f"\n\nBus Stop Code: {bus_stop}\nBus List: "

            for bus_service_no in user_data[bus_stop]:
                reply += f"{bus_service_no} "
        
    if (reply == ""):
        reply = "No buses or bus stops added. /add to start tracking buses."
    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['deleteBusStop'])
def delete_bus_stop(message):
    user_id = str(message.from_user.id)
    string = "Which bus stop(s) would you like to remove?\n"

    with shelve.open('busDB') as db:
        for bus_stop in db[user_id]:
            string += f"{bus_stop}\n"


    markup = types.ForceReply(selective=False)
    sent = bot.send_message(message.chat.id, string, reply_markup=markup)
    bot.register_next_step_handler(sent, process_delete_bus_stop)

def process_delete_bus_stop(reply):
    bus_stop_raw = reply.text
    bus_stops = bus_stop_raw.split()
    
    user_id = str(reply.from_user.id)
    deleted_string = ""
    with shelve.open('busDB', writeback=True) as db:
        for bus_stop in bus_stops:
            try:
                del db[user_id][bus_stop] #deletes the whole busstop
                deleted_string += bus_stop
                deleted_string += " "
            except Exception as e:
                print(f"Failed to delete bus stop {bus_stop}, {e}")
    if (deleted_string != ""):
        bot.send_message(reply.chat.id, f"Successfully deleted bus stop(s): {deleted_string}")
    else:
        bot.send_message(reply.chat.id, f"No bus stops were modified, key error?")


if __name__ == "__main__":
    main()
