import os
import re
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from helpers import gDrive_sql as db
from plugins.main import humanbytes
from plugins.token import getIdFromUrl
from helpers import parent_id_sql as sql
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
G_DRIVE_FILE_LINK = "https://drive.google.com/open?id={}"
G_DRIVE_FOLDER_LINK = "https://drive.google.com/drive/folders/{}"

def getFilesByFolderId(service, folder_id: str):
    page_token = None
    q = f"'{folder_id}' in parents"
    files = []
    while True:
        response = service.files().list(
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            q=q,
            spaces='drive',
            pageSize=200,
            fields='nextPageToken, files(id, name, mimeType, size)',
            pageToken=page_token
        ).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return files

def copyFile(service, file_id: str, dest_id: str):
    body = {'parents': [dest_id]}
    try:
        res = service.files().copy(
            supportsAllDrives=True,
            fileId=file_id,
            body=body
        ).execute()
        return res
    except HttpError as err:
        try:
            reason = json.loads(err.content).get('error', {}).get('errors', [{}])[0].get('reason', '')
            if reason in ['userRateLimitExceeded', 'dailyLimitExceeded']:
                return 'LimitExceeded'
            return 'error'
        except Exception:
            return 'error'

def create_directory(service, directory_name: str, parent_id: str = None):
    file_metadata = {
        "name": directory_name,
        "mimeType": G_DRIVE_DIR_MIME_TYPE
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]
    file = service.files().create(
        supportsAllDrives=True,
        body=file_metadata,
        fields="id"
    ).execute()
    return file.get("id")

def cloneFolder(service, name: str, local_path: str, folder_id: str, parent_id: str, transferred_size: int):
    files = getFilesByFolderId(service, folder_id)
    new_id = None
    if not files:
        return parent_id, transferred_size
    for file in files:
        if file.get('mimeType') == G_DRIVE_DIR_MIME_TYPE:
            file_path = os.path.join(local_path, file.get('name'))
            current_dir_id = create_directory(service, file.get('name'), parent_id)
            new_id, transferred_size = cloneFolder(service, file.get('name'), file_path, file.get('id'), current_dir_id, transferred_size)
        else:
            try:
                transferred_size += int(file.get('size', 0))
            except (TypeError, ValueError):
                pass
            result = copyFile(service, file.get('id'), parent_id)
            if result in ('LimitExceeded', 'error'):
                return 'error', transferred_size
            new_id = parent_id
    return new_id, transferred_size

@Client.on_message(filters.private & filters.command(['copy']))
async def _copy(client: Client, message: Message):
    creds = db.get_credential(message.from_user.id)
    if creds is None:
        await message.reply_text(
            '❗ **Not an authorized user.**\n__Authorize your Google Drive Account by running /auth Command in order to use this bot.__',
            quote=True
        )
        return

    parent_data = sql.get_id(message.from_user.id)
    parent_id = parent_data.parent_id if parent_data else 'root'
    transferred_size = 0

    if len(message.command) > 1:
        sent_message = await message.reply_text('**Checking Google Drive Link...**', quote=True)
        file_id = getIdFromUrl(message.command[1])
        if file_id == 'NotFound':
            await sent_message.edit('❗ **Invalid Google Drive URL**\n__Only Google Drive links can be copied.__')
            return
        await sent_message.edit(f'🗂️ **Cloning to Google Drive...**\n__{file_id}__')

        try:
            service = build(
                "drive",
                "v3",
                credentials=creds,
                cache_discovery=False
            )
        except Exception as e:
            await sent_message.edit(f"**ERROR:** Could not initialize Google Drive service.\n```{e}```")
            return

        try:
            meta = service.files().get(
                supportsAllDrives=True,
                fileId=file_id,
                fields="name,id,mimeType,size"
            ).execute()
        except HttpError as err:
            try:
                reason = json.loads(err.content).get('error', {}).get('errors', [{}])[0].get('reason', '')
            except Exception:
                reason = ''
            if 'notFound' in reason:
                await sent_message.edit(
                    '❗**ERROR: FILE NOT FOUND**\n__Make sure the file exists and is accessible by the account you authenticated.__'
                )
            else:
                await sent_message.edit(
                    f"**ERROR:** ```{str(err).replace('>', '').replace('<', '')}```"
                )
            return
        except Exception as e:
            await sent_message.edit(f"**ERROR:** ```{str(e).replace('>', '').replace('<', '')}```")
            return

        if meta.get("mimeType") == G_DRIVE_DIR_MIME_TYPE:
            dir_id = create_directory(service, meta.get('name'), parent_id)
            try:
                result, transferred_size = cloneFolder(
                    service,
                    meta.get('name'),
                    meta.get('name'),
                    meta.get('id'),
                    dir_id,
                    transferred_size
                )
                if result == 'error':
                    await sent_message.edit('**ERROR:** Could not copy some files or hit Google Drive limit.')
                    return
                await sent_message.edit(
                    f"✅ **Copied successfully.**\n[{meta.get('name')}]({G_DRIVE_FOLDER_LINK.format(dir_id)}) __({humanbytes(transferred_size)})__"
                )
            except Exception as e:
                await sent_message.edit(f'**ERROR:** ```{e}```')
        else:
            try:
                file = copyFile(service, meta.get('id'), parent_id)
                if file == 'LimitExceeded':
                    await sent_message.edit('❗**ERROR: Quota or rate limit exceeded. Try again later.**')
                    return
                if file == 'error' or not isinstance(file, dict):
                    await sent_message.edit('❗**ERROR: Could not copy the file.**')
                    return
                await sent_message.edit(
                    f"✅ **Copied successfully.**\n[{file.get('name')}]({G_DRIVE_FILE_LINK.format(file.get('id'))}) __({humanbytes(int(meta.get('size', 0)))})__"
                )
            except Exception as e:
                await sent_message.edit(f'**ERROR:** ```{e}```')
    else:
        await message.reply_text(
            '**Copy Google Drive Files or Folder**\n'
            '__Copy GDrive Files/Folder to your Google Drive Account. Use__\n'
            '```/copy {GDriveFolderURL or FileURL}``` __for copying.__'
        )
