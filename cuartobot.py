from asyncore import dispatcher
import os
import sys
import logging
from tokenize import group
from turtle import update #Para ver lo que hace es bot
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


#ACTIVAR EL TOKEN DESDE EL CMD : set TOKEN="el token".

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" 
)
logger = logging.getLogger()

TOKEN = os.getenv("TOKEN")

eventos = "El evento es:"  #variable para guardar info del evento.

def getBotInfo(update, context):
    bot = context.bot
    chatId = update.message.chat_id
    userName = update.effective_user["first_name"]
    logger.info(f'El usuario {userName} ha solicitado informacion del bot')
    bot.sendMessage(
        chat_id = chatId,
        parse_mode = "HTML",  #agregar negrita etc.
        text = f'Hola, soy un bot. <b>No molestar!</b>'

    )

def start(update, context):
    bot = context.bot
    userName = update.effective_user["first_name"]
    update.message.reply_text(f'Hola {userName} gracias por invocarme')


def welcomeMsg(update, context):
    bot = context.bot
    chatId = update.message.chat_id
    updateMsg = getattr(update, "message", None)
    for user in updateMsg.new_chat_members:
        userName = user.first_name

    logger.info(f'El usuario {userName} ha ingresado al grupo')

    bot.sendMessage(
        chat_id = chatId,
        parse_mode = "HTML",  #agregar negrita etc.
        text = f'Bienvenido al grupo {userName} \n Que la fuerza te acompañe.'
    )

def deleteMessage(bot, chatId, messageId, userName):
    try:
        bot.delete_message(chatId, messageId)
        logger.info(f'El mensaje de {userName} se borro por malas palabras')
    except Exception as e:
        print(e)


def echo(update, context):
    bot = context.bot
    updateMsg = getattr(update, "message", None)
    messageId = updateMsg.message_id  #obtener el id del mensaje.
    chatId = update.message.chat_id
    userName = update.effective_user["first_name"]
    text = update.message.text #obtener el texto que envio el usuario.
    logger.info(f'El usuario {userName} ha enviado un nuevo mensaje al grupo {chatId}')

    badWord = 'baboso'
    if badWord in text:
        deleteMessage(bot, chatId, messageId, userName)
        bot.sendMessage(
        chat_id = chatId,
        text = f'El mensaje de {userName} fue eliminado por malas palabras.'
    )
    elif 'bot' in text and 'hola' in text:
        bot.sendMessage(
        chat_id = chatId,
        text = f'Hola {userName} no soy un bot.'
    )

def userisAdmin(chatId, userId, bot):
    try:
        groupAdmins = bot.get_chat_administrators(chatId)
        for admin in groupAdmins:
            if admin.user.id == userId:
                isAdmin = True
            else:
                isAdmin = False

        return isAdmin
    except Exception as e:
        print(e)

def addEvent(update, context):
    global eventos
    bot = context.bot
    chatId = update.message.chat_id
    userName = update.effective_user["first_name"]
    userId = update.effective_user["id"]
    args = context.args  # argumentos que pasó el usuario


    if userisAdmin(chatId, userId, bot) == True:
        if len(args) == 0:
            logger.info(f'El usuario {userName} no ha ingresado argumento')
            bot.sendMessage(
                chat_id = chatId,
                text = f'{userName} Ingrese mas info para agregar el evento.'
            )
        else:
            evento = " ".join(args)
            eventos = eventos + "\n>>" + evento

            logger.info(f'El usuario {userName}  ha ingresado un nuevo evento')

            bot.sendMessage(
                chat_id = chatId,
                text = f'{userName} has ingresado un evento correctamente.'
            )
    else:
        logger.info(f'{userName}  ha intentado agregar un nuevo evento pero no tiene permisos')

        bot.sendMessage(
            chat_id = chatId,
            text = f'{userName} no tienes permisos para agregar un evento.'
        )

def event(update, context):
    bot = context.bot
    chatId = update.message.chat_id
    userName = update.effective_user["first_name"]

    logger.info(f'El usuario {userName} ha solicitado los eventos')
    bot.sendMessage(
        chat_id = chatId,
        text = eventos
    )



if __name__ == "__main__":
    #obtener la informacion del bot
    myBot = telegram.Bot(token = TOKEN)
    #print(myBot.getMe())

#updater se conecta y recibe los mensajes

update = Updater(myBot.token, use_context=True)

#Crear dispatcher

dp = update.dispatcher

#Crear command

dp.add_handler(CommandHandler("botInfo", getBotInfo)) 
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("addEvent", addEvent, pass_args=True))
dp.add_handler(CommandHandler("event", event))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcomeMsg))
dp.add_handler(MessageHandler(Filters.text, echo)) #El bot va leer los mensajes.
 



update.start_polling()  #Se preguntar por los mensajes entrantes.
print("Bot Running")
update.idle()  #Cerrar el bot con Ctrl + c
