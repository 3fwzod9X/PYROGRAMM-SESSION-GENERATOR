import os
import asyncio
from pyrogram import Client, filters
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api_id = "10412514"
api_hash = "4d55a7064ad72adcfa8944f505453a8c"
bot_token = os.environ.get('BOT_TOKEN', '6182287341:AAFhYl99bc82mDQg7t6VaExxD_9Ds2q3wbs')

pyro_client = Client(":memory:", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
tel_client = TelegramClient(StringSession(), api_id=api_id, api_hash=api_hash)


@pyro_client.on_message(filters.command('start'))
async def start_command_handler(client, message):
    await message.reply('Hi, I can help you generate Pyrogram and Telethon string sessions. Please select an option:',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton('Pyrogram', callback_data='pyro'),
                            InlineKeyboardButton('Telethon', callback_data='tel')
                        ]]))


@pyro_client.on_callback_query()
async def callback_handler(client, query):
    if query.data == 'pyro':
        chat_id = query.message.chat.id
        await client.send_message(chat_id, 'Please enter your phone number (with country code):')
        await pyro_client.register_next_step_handler(query.message, process_pyro_phone_number)
    elif query.data == 'tel':
        chat_id = query.message.chat.id
        await client.send_message(chat_id, 'Please enter your phone number (with country code):')
        await pyro_client.register_next_step_handler(query.message, process_tel_phone_number)


async def process_pyro_phone_number(message):
    chat_id = message.chat.id
    phone_number = message.text

    try:
        await pyro_client.start(phone_number=phone_number)
    except Exception as e:
        await pyro_client.send_message(chat_id, f'Error starting client: {str(e)}')
        return

    try:
        code = await pyro_client.send_code(phone_number)
    except Exception as e:
        await pyro_client.send_message(chat_id, f'Error sending code: {str(e)}')
        return

    await pyro_client.send_message(chat_id, 'Please enter the code (without spaces):')
    code_text = await pyro_client.wait_for_message(chat_id=chat_id)

    try:
        await pyro_client.sign_in(phone_number, code.phone_code_hash, code_text.text)
    except Exception as e:
        if "SESSION_PASSWORD_NEEDED" in str(e):
            await pyro_client.send_message(chat_id, 'Please enter your password:')
            password = await pyro_client.wait_for_message(chat_id=chat_id)

            try:
                await pyro_client.check_password(password.text)
                await pyro_client.sign_in(phone_number, code.phone_code_hash, code_text.text, password=password.text)
            except Exception as e:
                await pyro_client.send_message(chat_id, f'Error signing in: {str(e)}')
                return
        else:
            await pyro_client.send_message(chat_id, f'Error signing in: {str(e)}')
            return

    session_string = await pyro_client.export_session_string()
    await pyro_client.send_message(chat_id, f'Here is your Pyrogram session string:\n\n```\n{session_string}\n```')


async def process_tel_phone_number(message):
    chat_id = message.chat.id
    phone_number = message.text

    try:
        await tel_client.connect()
    except Exception as e:
        await tel_client.send_message(chat_id, f'Error connecting client: {str(e)}')
        return

    if not await tel_client.is_user_authorized():
        try:
            await tel_client.send_code_request(phone_number)
        except Exception as e:
            await tel_client.send_message(chat_id, f'Error sending code request: {str(e)}')
            return

        await tel_client.send_message(chat_id, 'Please enter the code (without spaces):')
        code_text = await tel_client.wait_for_message(chat_id=chat_id)

        try:
            await tel_client.sign_in(phone_number, code_text.text)
        except Exception as e:
            if "SESSION_PASSWORD_NEEDED" in str(e):
                await tel_client.send_message(chat_id, 'Please enter your password:')
                password = await tel_client.wait_for_message(chat_id=chat_id)

                try:
                    await tel_client.check_password(password.text)
                    await tel_client.sign_in(phone_number, code_text.text, password=password.text)
                except Exception as e:
                    await tel_client.send_message(chat_id, f'Error signing in: {str(e)}')
                    return
            else:
                await tel_client.send_message(chat_id, f'Error signing in: {str(e)}')
                return

    session_string = tel_client.session.save()
    await tel_client.send_message(chat_id, f'Here is your Telethon session string:\n`{session_string}`')


asyncio.get_event_loop().run_until_complete(pyro_client.start())
