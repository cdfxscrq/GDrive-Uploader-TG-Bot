import os 
import math
import wget
import json
import time
import asyncio
from pyrogram import Client, Filters
from config import Messages as tr
from config import Config
from mimetypes import guess_type
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


async def upload_file(creds, file_path, filesize, parent_id, message):
    service = build(
        "drive",
        "v3",
        credentials=creds,
        cache_discovery=False
    )
    mime_type = guess_type(file_path)[0]
    mime_type = mime_type if mime_type else "text/plain"
    media_body = MediaFileUpload(
        file_path,
        mimetype=mime_type,
        chunksize=150*1024*1024,
        resumable=True
    )
    file_name = os.path.basename(file_path)
    await message.edit(f'📤 **Uploading...**\n**Filename:** ```{file_name}```\n**Size:** ```{filesize}```')
    body = {
        "name": file_name,
        "description": "Uploaded Successfully",
        "mimeType": mime_type,
    }
    if parent_id:
      body["parents"] = [parent_id]
    try:
      uploaded_file = service.files().create(body=body, media_body=media_body, fields='id', supportsTeamDrives=True).execute()
      file_id = uploaded_file.get('id')
      return file_id
    except HttpError as err:
      if err.resp.get('content-type', '').startswith('application/json'):
        reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
        if reason == 'userRateLimitExceeded' or reason == 'dailyLimitExceeded':
          return 'LimitExceeded'
        else:
          await message.reply_text(f"{err.replace('<', '').replace('>', '')}")
    except Exception as e:
      await message.reply_text(f'**ERROR:** ```{e}```', quote=True)
      return 'error'