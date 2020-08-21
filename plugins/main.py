import os
import math
import wget
import time
import asyncio
from pyrogram import Client, Filters
from config import Config
from pySmartDL import SmartDL
from plugins.uploader import upload_file
from helpers import gDrive_sql as db
from helpers import parent_id_sql as sql
from urllib.error import HTTPError

@Client.on_message(Filters.private & Filters.incoming & (Filters.audio | Filters.photo | Filters.video | Filters.document | Filters.regex('^(ht|f)tp*')))
async def _start(client, message):
  creds = db.get_credential(message.from_user.id)
  if creds is None:
    await message.reply_text("🔑 **You have not authenticated me to upload to any account.**\n__Send /auth to authenticate.__", quote=True)
    return
  if sql.get_id(message.from_user.id):
    parent_id = sql.get_id(message.from_user.id).parent_id
  else:
    parent_id = None
  if message.text:
    if message.text.startswith('http'):
      sent_message = await message.reply_text('**Checking Link...**', quote=True)
      filename = await download_file(client, message, sent_message)
      if filename in ("HTTPError"):
        await sent_message.edit('**❗ Invalid URL**\n__Make sure it\'s a direct link and in working state.__')
        return
  elif message.media:
    sent_message = await message.reply_text('📥 **Downloading File...**', quote=True)
    try:
      filename = await client.download_media(message=message)
    except Exception as e:
      sent_message.edit(f'**ERROR:** ```{e}```')
  filesize = humanbytes(os.path.getsize(filename))
  file_name = os.path.basename(filename)
  await sent_message.edit(f'✅ **Download Completed**\n**Filename:** ```{file_name}```\n**Size:** ```{filesize}```\n__Now starting upload...__')
  file_id = await upload_file(
        creds=creds,
        file_path=filename,
        filesize=filesize,
        parent_id=parent_id,
        message=sent_message)
  if file_id not in ('error', 'LimitExceeded'):
    await sent_message.edit("✅ **Uploaded Successfully.**\n<a href='https://drive.google.com/open?id={}'>{}</a> __({})__".format(file_id, file_name, filesize))
  elif file_id == 'LimitExceeded':
    await sent_message.edit('❗ **Upload limit exceeded**\n__Try after 24 hours__')
  else:
    await sent_message.edit('❗ **Uploading Error**\n__Please try again later.__')
  os.remove(filename)

async def download_file(client, message, sent_message):
  seperate_url = "".join(message.text)
  url = seperate_url.strip()
  custom_file_name = os.path.basename(url)
  dl_path = os.path.join('downloads/')
  if "|" in seperate_url:
    url, custom_file_name = seperate_url.split("|")
    url = url.strip()
    custom_file_name = custom_file_name.strip()
    dl_path = os.path.join(f"downloads/{custom_file_name}")
  try:
    dl = SmartDL(url, dl_path, progress_bar=False)
    await sent_message.edit(f'📥 **Downloading...**\n**Filename:** ```{custom_file_name}```')
    dl.start()
    return dl.get_dest()
  except HTTPError:
    return 'HTTPError'
    await sent_message.reply_text(url)
  except Exception as e:
    await sent_message.edit(f'📥 **Downloading...**\n**Filename:** ```{custom_file_name}```\n__Downloader failed trying again.__')
    try:
      filename = wget.download(url, dl_path)
      return os.path.join(f"downloads/{filename}")
    except HTTPError:
      return 'HTTPError'
      await sent_message.reply_text(url)


def humanbytes(size: int) -> str:
    if not size:
        return ""
    power = 2 ** 10
    number = 0
    dict_power_n = {
        0: " ",
        1: "K",
        2: "M",
        3: "G",
        4: "T",
        5: "P"
    }
    while size > power:
        size /= power
        number += 1
    return str(round(size, 2)) + " " + dict_power_n[number] + 'B'