import json # parse JSON responses from Telegram into Python dictionaries
import requests # make web requests and interact with Telegram API
import time 
import urllib # encode any special characters
from dbhelper import DBHelper # import DBHelper class defined in dbhelper.py script
from PIL import Image
import telegram 

db = DBHelper() # we can access the methods to get, add, and delete items through the db variable

TOKEN = "968019501:AAHTsOYy26wr-n4f_3XBk_o78-gcPtbB8SA" # define our Bot's token that we need to authenticate with the Telegram API
URL = "https://api.telegram.org/bot{}/".format(TOKEN) #  create the basic URL that we'll be using in all our requests to the API

bot = telegram.Bot(token = TOKEN)

'''
# store graph images generated from matplotlib into variables
pollutant_pm25 = Image.open("pm25.png")
pollutant_o3 = Image.open("o3.png")
pollutant_co = Image.open("co.png")
pollutant_so2 = Image.open("so2.png")
pollutant_no2 = Image.open("no2.png")
pollutant_pm10 = Image.open("pm10.png")
'''

def get_url(url):
    # simply downloads the content from a URL and gives us a string
    response = requests.get(url) 
    content = response.content.decode("utf8") # for extra compatibility
    # no exception handling, assume everything always works 
    return content


def get_json_from_url(url):
    # gets the string response as above and parses this into a Python dictionary using json.loads (load string)
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    # calls the same API command that we used in our browser earlier, and retrieves a list of "updates" (messages sent to our Bot). 
    # offset indicate that we don't want to receive any messages with smaller IDs than this
    url = URL + "getUpdates?timeout=100" # long polling keeps the connection open until there are updates. Since it's impractical to open forever, wait 100s.
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    # calculates the highest ID of all the updates we receive from getUpdates
    update_ids = []
    # loops through each of the updates that we get from Telegram and then returns the biggest ID
    # We need this so that we can call getUpdates again, passing this ID, and indicate which messages we've already seen.
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)



def handle_updates(updates):
    # loop through each update and grab the text and the chat components 
    # so that we can look at the text of the message we received and respond to the user who sent it.
    def send_photo(pollutant):
        bot.send_photo(chat, photo=open(pollutant + '.png', 'rb'))
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)  # load the items of a particular chat id from our database  and store them in the items variable
        print()
        # check message
        if text == "/pollutants": # send the custom keyboard to the user whenever they indicate that they want to mark items as done
            keyboard = build_keyboard()
            send_message("Select a pollutant", chat, keyboard)
        elif text == "pm25":
            send_photo("pm25")
        elif text == "o3":
            send_photo("o3")
        elif text == "co":
            send_photo("co")
        elif text == "so2":
            send_photo("so2")
        elif text == "no2":
            send_photo("no2")
        elif text == "pm10":
            send_photo("pm10")
        elif text == "/start":
            send_message("Welcome to your personal To Do list. Send any text to me and I'll store it as an item. Send /done to remove items", chat)
        elif text.startswith("/"):
            continue
        elif text in items: # send the keyboard along after the user has just marked off an item, so several items can easily be deleted in a row
            db.delete_item(text, chat)  ##
            items = db.get_items(chat)  ##
            keyboard = build_keyboard()
            send_message("Select an item to delete", chat, keyboard)
        else:
            db.add_item(text, chat)  ##
            items = db.get_items(chat)  ##
            message = "\n".join(items)
            send_message(message, chat)


def get_last_chat_id_and_text(updates):
    # provides a simple but inelegant way to get the chat ID and the message text of the most recent message sent to our Bot.
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def build_keyboard():
	# take a list of items and construct a keyboard to allow the user to easily delete the items
    keyboard = [['pm25', 'o3', 'co'],
                   ['so2', 'no2', 'pm10']]
	# build a dictionary which contains the keyboard as a value to the "keyboard" key and 
	# specifies that this keyboard should disappear once the user has made one choice
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup) # convert the Python dictionary to a JSON string, as this is the format that Telegram's API expects from us.


def send_message(text, chat_id, reply_markup=None):
    # takes the text of the message we want to send (text) and the chat ID of the chat where we want to send the message (chat_id).
    # It then calls the sendMessage API command, passing both the text and the chat ID as URL parameters, thus asking Telegram to send the message to that chat.
	# add the keyboard as an optional parameter to this function, and if it's included we'll pass along the keyboard with the rest of the API call
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)
    
def main():
    # gets the most recent messages from Telegram every half second
    # remember the most recent message that we replied to (we save this in the last_textchat variable) 
    # so that we don't keep on sending the echoes every second to messages that we've already processed
    db.setup() # # creates a new table called items in our database. This table has one column (called description)
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)



if __name__ == '__main__':
    main()