from lxml import html
import telebot
import requests
import datetime
import json

#	------------------------------------------------------------------------------------------
#								/* Description: Telegram Bot
#								/* Author: R3m0tEe						
#								/* Last updated on: Mon August, 30 2021
#								/* @Github: https://github.com/R3m0tEe
#
# 						//////////////////////////////////////////////////////
#
#			 						Steps to reproduce:
# 						1) Create a Telegram bot using BotFather
# 						2) Copy it's API KEY (API Token)
#			 			4) Paste it in line 23
#						5) Add the created bot in a Group in Telegram
#						6) Run this script


API_KEY = "[PASTE YOUR API KEY HERE]"

bot = telebot.TeleBot(API_KEY)

commands = {  # Command description used in the "help" command
	'hello'		: 'Say Hi to the bot',
	'date'		: "Display today's date",
	'weather'		: 'Display current''s location weather',
	'ict_news'		: 'Display most recent news from "Τμήμα Μηχανικών Πληροφορικής, Υπολογιστών και Τηλεπικοινωνιών"',
	'foititika_nea': 'Display most recent news from "Foititika Nea"'
}

user_dict = {}

class User:
	def __init__(self, location):
		self.location = location


@bot.message_handler(commands=['hello','Hello','hi','Hi'])
def hello(message):
	bot.reply_to(message,"Hello there!")

@bot.message_handler(commands=['help','Help'])
def help(message):
	cid = message.chat.id
	help_text = "Hi! The following commands are available: \n\n"
	for key in commands:
		help_text += "/" + key + ": "
		help_text += commands[key] + "\n"
	bot.send_message(cid, help_text)  # send the generated help page

@bot.message_handler(commands=['ict_news','Ict_news','Ict_News'])
def ict_news(message):
	# Send Request and parse HTML
	page = requests.get('http://ict.ihu.gr/')
	tree = html.fromstring(page.content)
	# Extract text from specific website using XPATH
	temp_list = ["Πρόσφατες Ανακοινώσεις:\n---------------------------------------"]
	perma_list = ["Μόνιμες Ανακοινώσεις:\n-----------------------------------"]
	for i in range(4):
		recent_news = tree.xpath('//*[@id="eael-post-grid-ee1b055"]/div[1]/article[' + str(i+1) +']/div/div/div/header/h2/a')
		link = recent_news[0].get('href')
		link_f = " " + link + "/"
		temp_list.append(str(i+1) + ") " + recent_news[0].text + link_f)
		final_temp_news = '\n'.join(temp_list)
	bot.send_message(message.chat.id,final_temp_news,disable_web_page_preview=True)
	for i in range(4):
		perma_news = tree.xpath('//*[@id="eael-post-grid-0363165"]/div[1]/article[' + str(i+1) +']/div/div/div/header/h2/a')
		link = perma_news[0].get('href')
		link_f = " " + link + "/"
		perma_list.append(str(i+1) + ") " + perma_news[0].text + link_f)
		final_perma_news = '\n'.join(perma_list)
	bot.send_message(message.chat.id,final_perma_news,disable_web_page_preview=True)

@bot.message_handler(commands=['foititika_nea','Foititika_nea',"Foititika_Nea"])
def foititika_nea(message):
	# Send Request and parse HTML
	page = requests.get('https://foititikanea.gr/')
	tree = html.fromstring(page.content)
	# Extract text from specific website using XPATH
	foiti_nea_list = ["Τελευταία Φοιτητικά Νέα - Ροή Ειδήσεων:\n--------------------------------------------------------------"]
	for i in range(5):
		recent_news = tree.xpath('//*[@id="content"]/div[3]/div[' + str(i+1) + ']/div/div[1]/h2/a')
		link = recent_news[0].get('href')
		link_f = "https://foititikanea.gr" + link + "/"
		foiti_nea_list.append(str(i+1) + ") " + recent_news[0].text + link_f)
		final_foiti_nea_list = '\n'.join(foiti_nea_list)
	bot.send_message(message.chat.id,final_foiti_nea_list,disable_web_page_preview=True)

@bot.message_handler(commands=['date','Date'])
def date(message):
	date_time = datetime.datetime.now()
	d = date_time.strftime("%Y-%b-%d %H:%M")
	bot.send_message(message.chat.id,d)

@bot.message_handler(commands=['weather'])
def weather(message):
	msg = bot.reply_to(message, """\
Hi there,
Please type your location:
""")
	bot.register_next_step_handler(msg, process_weather_step)

def tell_weather(userlocation):
	try:
		url = 'https://openweathermap.org/data/2.5/weather?q=' + userlocation + '&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric'
		r = requests.get(url)
		j = r.json()
		temp ="Temperature: {}°C ".format(j['main']['temp'])
		wind_speed = "Wind speed: {} m/s".format(j['wind']['speed'])
		desc = "Description: {}".format(j['weather'][0]['description'])
		weather = "Weather: {}".format(j['weather'][0]['main'])
		conc = temp + '\n' + wind_speed + '\n'+  desc + '\n' + weather 
		return(conc)
	except:
		return ("Ooops. Something went wrong!")

def process_weather_step(message):
	try:
		chat_id = message.chat.id
		location = message.text
		user = User(location)
		user_dict[chat_id] = user
		cap_string = user.location.capitalize()
		url = 'https://openweathermap.org/data/2.5/weather?q=' + cap_string + '&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric'
		r = requests.get(url)
		if r.status_code == 200:
			bot.send_message(chat_id, 'The weather for ' + cap_string + ':\n-------------------------------------------\n' + tell_weather(cap_string))
		else:
			bot.reply_to(message, 'City name not found...')
	except Exception as e:
		bot.reply_to(message, 'Ooops. Something went wrong!')

bot.polling()