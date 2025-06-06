import os
import json
import time
from mimetypes import guess_type
from pyrogram import Client, filters
from config import Messages as tr
from config import Config
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from pyrogram.types import Message

async def upload_file(
    creds,
    file_path: str,
    filesize: int,
    parent_id: str,
    message: Message
) -> str:
    """
    Uploads a file to Google Drive.
    Returns the file ID if successful, 'LimitExceeded' for rate/daily limits, or 'error' for other errors.
    """
    try:
        service = build(
            "drive",
            "v3",
            credentials=creds,
            cache_discovery=False
        )

        mime_type = guess_type(file_path)[0] or "application/octet-stream"
        media_body = MediaFileUpload(
            file_path,
            mimetype=mime_type,
            chunksize=150 * 1024 * 1024,
            resumable=True
        )
        file_name = os.path.basename(file_path)
        await message.edit_text(
            f'📤 **Uploading...**\n**Filename:** ```{file_name}```\n**Size:** ```{filesize}```'
        )
        body = {
            "name": file_name,
            "description": "Uploaded Successfully",
            "mimeType": mime_type,
        }
        if parent_id:
            body["parents"] = [parent_id]

        uploaded_file = service.files().create(
            body=body,
            media_body=media_body,
            fields='id',
            supportsAllDrives=True  # Updated param: supportsTeamDrives is deprecated
        ).execute()
        file_id = uploaded_file.get('id')
        return file_id

    except HttpError as err:
        try:
            error_content = json.loads(err.content)
            reason = error_content.get('error', {}).get('errors', [{}])[0].get('reason')
            if reason in ('userRateLimitExceeded', 'dailyLimitExceeded'):
                return 'LimitExceeded'
            else:
                await message.reply_text(f"Google API Error: {reason}")
        except Exception as e:
            await message.reply_text(f"Google API Error: {err}")
        return 'error'
    except Exception as e:
        await message.reply_text(f'**ERROR:** ```{e}```', quote=True)
        return 'error'
