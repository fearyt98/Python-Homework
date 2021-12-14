import telebot
import urllib.request
from telebot import types
import time
import re

#Создаем экземпляр бота
bot = telebot.TeleBot("")

#Разметка для калькулятора
keyboard = telebot.types.InlineKeyboardMarkup()
keyboard.row(telebot.types.InlineKeyboardButton(" ", callback_data="None"),
                 telebot.types.InlineKeyboardButton("C", callback_data="C"),
                 telebot.types.InlineKeyboardButton("<=", callback_data="<="),
                 telebot.types.InlineKeyboardButton("/", callback_data="/"))

keyboard.row(telebot.types.InlineKeyboardButton("7", callback_data="7"),
                 telebot.types.InlineKeyboardButton("8", callback_data="8"),
                 telebot.types.InlineKeyboardButton("9", callback_data="9"),
                 telebot.types.InlineKeyboardButton("*", callback_data="*"))

keyboard.row(telebot.types.InlineKeyboardButton("4", callback_data="4"),
                 telebot.types.InlineKeyboardButton("5", callback_data="5"),
                 telebot.types.InlineKeyboardButton("6", callback_data="6"),
                 telebot.types.InlineKeyboardButton("-", callback_data="-"))

keyboard.row(telebot.types.InlineKeyboardButton("1", callback_data="1"),
                 telebot.types.InlineKeyboardButton("2", callback_data="2"),
                 telebot.types.InlineKeyboardButton("3", callback_data="3"),
                 telebot.types.InlineKeyboardButton("+", callback_data="+"))

keyboard.row(telebot.types.InlineKeyboardButton(" ", callback_data="None"),
                 telebot.types.InlineKeyboardButton("0", callback_data="0"),
                 telebot.types.InlineKeyboardButton(".", callback_data="."),
                 telebot.types.InlineKeyboardButton("=", callback_data="="))
value = ""
old_value = ""

#Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(message, res=False):
    #Клавиатура для бота
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Проверка доступности сайта")
    item2=types.KeyboardButton("Анализ текста")
    item3=types.KeyboardButton("Калькулятор")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    bot.send_message(message.chat.id, "Выберите задачу", reply_markup=markup)

# Получение сообщений от пользователя
@bot.message_handler(content_types=["text"])
def handle_menu_text(message):
    if message.text.strip() == "Проверка доступности сайта":
        if urllib.request.urlopen("https://www.stackoverflow.com").getcode() == 200:
            bot.send_message(message.chat.id, 'Сайт Stackoverflow доступен')
        else:
            bot.send_message(message.chat.id, 'Сайт Stackoverflow не доступен')
    elif message.text.strip() == "Анализ текста":
        bot.register_next_step_handler(message, text_anylize)
        bot.send_message(message.chat.id, 'Введите текст:')
    elif message.text.strip() == "Калькулятор":
        bot.send_message(message.chat.id, "Это калькулятор", reply_markup=keyboard)

#Функция обработки запросов для кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback(query):
    global value, old_value
    #Обработка переданных данных, если они имеют ключевые символы
    data = query.data
    if data == "None":
        pass
    elif data == "C":
        value = ""
    elif data == "<=":
        if value != '':
            value = value[0:len(value)-1] #Удаление одного символа из строки
    elif data == "=":
        try:
            value = str(eval(value)) #Выполнение расчета (2+2) и т.д.
        except:
            value = "Ошибка ввода"
    else:
        value += data

    if (value != old_value and value != "") or (old_value !=  "0" and value == ""):
        if value == "":
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text='0', reply_markup=keyboard)
            old_value = "0"
        else:
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=value, reply_markup=keyboard)
            old_value = value

    if value == "Ошибка ввода":
        value = ""

def text_anylize(message):    
    lines = re.split("[.!?]", message.text)
    length_message = len(message.text)

#Убираем пробелы вначале предложения и удаляем пустые строки (или состоящие из 1 пробела)
    for i in range(len(lines)):
        words = lines[i]
        if lines[i] == '' or lines[i] == ' ':
            lines.pop(i)
        elif words[0] == " " and words != '':
            words = words[1:len(words)]
            lines[i] = words
        
#Очищаем предложения от других знаков препинания
    formated_lines = []
    for i in lines:
        formated_lines.append(str(i).replace(',',' ').replace('-','.').replace('—','.').replace('  ',' '))

#Создаем словарь из ключей в виде слов и значений - их количество
    dictionary = {}
    max_length_word = 0
    for j in formated_lines:
        line = j.split(' ')
        for k in line:
            if len(k.lower())>max_length_word:
                max_length_word = len(k)
            if dictionary.get(k.lower()) != None and k !='':
                value = dictionary.get(k.lower())
                value += 1
                dictionary[k.lower()] = value
            else:
                value = 1
                dictionary.update({k.lower():value})

#Определяем уникальные слова и популярное слово
    frequent_word = ""
    count = 0
    unique_words = 0

    for i in dictionary:
        if dictionary[i] == 1:
            unique_words+=1
        if dictionary[i]>count and (i != 'И' and i != 'и' and i != 'А' and i != 'а' and i != 'Но' and i != 'но'):
            count = dictionary[i]
            frequent_word = i

#Определяем статистику по словам - их вес и количество повторений
    stat = ""
    for i in dictionary:
        stat+= "Слово: "+i+"\nПовторений: "+str(dictionary[i])+" >> "+str(dictionary[i]*round((len(i)/length_message)*100, 2))+"% текста\n"

    #bot.send_message(message.chat.id, ""+str(dictionary))
    #time.sleep(1)
    bot.send_message(message.chat.id, "Наиболее популярное слово: "+str(frequent_word)+
    "\nКоличество уникальных слов: "+str(unique_words)+"\nКоличество предложений: "+str(len(lines))+"\n\n"+stat)
   
# Запускаем бота
bot.polling(none_stop=True, interval=0)