import os
import asyncio
from pyrogram import Client, filters
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

pyro_client = Client(":memory:", api_id, api_hash, bot_token=bot_token)
tel_client = TelegramClient(StringSession(), api_id, api_hash)


@pyro_client.on_message(filters.command('start'))
async def start_command_handler(client, message):
    await message.reply('Hi, I can help you generate Pyrogram and Telethon string sessions. Please select an option:',
                        reply_markup=types.InlineKeyboardMarkup([[
                            types.InlineKeyboardButton('Pyrogram', callback_data='pyro'),
                            types.InlineKeyboardButton('Telethon', callback_data='tel')
                        ]]))

@pyro_client.on_message(filters.command('pyro'))
async def pyro_command_handler(client, message):
    chat_id = message.chat.id
    await client.send_message(chat_id, 'Please enter your API ID:')
    api_id = await client.ask(chat_id)

    await client.send_message(chat_id, 'Please enter your API hash:')
    api_hash = await client.ask(chat_id)

    await client.send_message(chat_id, 'Please enter your phone number (with country code):')
    phone_number = await client.ask(chat_id)

    try:
        await client.start()
    except Exception as e:
        await client.send_message(chat_id, f'Error starting client: {str(e)}')
        return

    try:
        code = await client.send_code(phone_number.text)
    except Exception as e:
        await client.send_message(chat_id, f'Error sending code: {str(e)}')
        return

    await client.send_message(chat_id, 'Please enter the code (without spaces):')
    code_text = await client.ask(chat_id)

    try:
        await client.sign_in(phone_number.text, code.phone_code_hash, code_text.text)
        session_string = await client.export_session_string()
    except Exception as e:
        await client.send_message(chat_id, f'Error generating session string: {str(e)}')
        return

    await client.send_message(chat_id, f'Here is your Pyrogram session string:\n\n```\n{session_string}\n```')


@pyro_client.on_message(filters.command('tel'))
async def tel_command_handler(client, message):
    chat_id = message.chat.id
    await client.send_message(chat_id, 'Please enter your API ID:')
    api_id = await client.ask(chat_id)

    await client.send_message(chat_id, 'Please enter your API hash:')
    api_hash = await client.ask(chat_id)

    try:
        await tel_client.connect()
    except Exception as e:
        await client.send_message(chat_id, f'Error connecting client: {str(e)}')
        return

    if not await tel_client.is_user_authorized():
        await client.send_message(chat_id, 'Please enter your phone number (with country code):')
        phone_number = await client.ask(chat_id)

        try:
            await tel_client.send_code_request(phone_number.text)
        except Exception as e:
            await client.send_message(chat_id, f'Error sending code request: {str(e)}')
            return

        await client.send_message(chat_id, 'Please enter the code (without spaces):')
        code_text = await client.ask(chat_id)

        try:
            await tel_client.sign_in(phone_number.text, code_text.text)
        except Exception as e:
            await client.send_message(chat_id, f'Error signing in: {str(e)}')
            return

    session_string = tel_client.session.save()
    await client.send_message(chat_id, f'Here is your Telethon session string:\n`{session_string}`')

pyro_client.run()

