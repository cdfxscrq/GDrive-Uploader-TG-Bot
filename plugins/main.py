import os
import asyncio
from pyrogram import Client, filters
from config import Config
from pySmartDL import SmartDL
from plugins.uploader import upload_file
from helpers import gDrive_sql as db
from helpers import parent_id_sql as sql
from urllib.error import HTTPError
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")


@Client.on_message(
    filters.private
    & filters.incoming
    & (
        filters.audio
        | filters.photo
        | filters.video
        | filters.document
        | filters.regex(r"^(ht|f)tp[s]?://")
    )
)
async def _start(client, message):
    creds = db.get_credential(message.from_user.id)
    if creds is None:
        await message.reply_text(
            "🔑 **You have not authenticated me to upload to any account.**\n__Send /auth to authenticate.__",
            quote=True,
        )
        return

    parent_id = None
    user_parent = sql.get_id(message.from_user.id)
    if user_parent:
        parent_id = user_parent.parent_id

    filename = None
    sent_message = None

    if message.text and message.text.strip().startswith(("http", "ftp")):
        sent_message = await message.reply_text('**Checking Link...**', quote=True)
        filename = await download_file(message, sent_message)
        if filename == "HTTPError":
            await sent_message.edit(
                "**❗ Invalid URL**\n__Make sure it's a direct link and in working state.__"
            )
            return
        if not filename or not os.path.exists(filename):
            await sent_message.edit("❗ **Download failed. File not found.**")
            return
    elif message.media:
        sent_message = await message.reply_text('📥 **Downloading File...**', quote=True)
        try:
            filename = await client.download_media(message=message, file_name=DOWNLOAD_DIR)
        except Exception as e:
            await sent_message.edit(f'**ERROR:** ```{e}```')
            return

    if not filename or not os.path.exists(filename):
        if sent_message:
            await sent_message.edit("❗ **Download failed. File not found.**")
        return

    filesize = humanbytes(os.path.getsize(filename))
    file_name = os.path.basename(filename)
    await sent_message.edit(
        f'✅ **Download Completed**\n**Filename:** ```{file_name}```\n**Size:** ```{filesize}```\n__Now starting upload...__'
    )
    file_id = await upload_file(
        creds=creds,
        file_path=filename,
        filesize=filesize,
        parent_id=parent_id,
        message=sent_message,
    )
    if file_id not in ('error', 'LimitExceeded'):
        await sent_message.edit(
            f"✅ **Uploaded Successfully.**\n<a href='https://drive.google.com/open?id={file_id}'>{file_name}</a> __({filesize})__",
            disable_web_page_preview=True,
        )
    elif file_id == 'LimitExceeded':
        await sent_message.edit('❗ **Upload limit exceeded**\n__Try after 24 hours__')
    else:
        await sent_message.edit('❗ **Uploading Error**\n__Please try again later.__')

    try:
        os.remove(filename)
    except Exception:
        pass


async def download_file(message, sent_message):
    url = message.text.strip()
    custom_file_name = None
    dl_path = DOWNLOAD_DIR

    # Check for custom file name using '|'
    if "|" in url:
        url, custom_file_name = map(str.strip, url.split("|", 1))
        dl_path = DOWNLOAD_DIR / custom_file_name

    else:
        custom_file_name = os.path.basename(url)
        dl_path = DOWNLOAD_DIR / custom_file_name

    try:
        dl = SmartDL(url, str(dl_path), progress_bar=False)
        await asyncio.get_event_loop().run_in_executor(None, dl.start)
        return dl.get_dest()
    except HTTPError:
        return 'HTTPError'
    except Exception as e:
        await sent_message.edit(
            f'📥 **Downloading...**\n**Filename:** ```{custom_file_name}```\n__Downloader failed: {e}__'
        )
        return None


def humanbytes(size: int) -> str:
    """
    :param size: int
    :return: str
    Converts bytes to human-readable format
    """
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
    while size >= power and n < len(power_labels) - 1:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}B"
