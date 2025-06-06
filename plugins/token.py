import re
from httplib2 import Http
from pyrogram import Client
from pyrogram.filters import private, incoming, command, text
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from helpers import gDrive_sql as db
from helpers import parent_id_sql as sql

OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
G_DRIVE_CLIENT_ID = "197036948433-4sjgjrj1osm5b5neu8khh7c2nsvn96f7.apps.googleusercontent.com"
G_DRIVE_CLIENT_SECRET = "dnXoMIu2V7HQ8G8RicrKmvlu"

# Store per-user OAuth flows
user_flows = {}

@Client.on_message(private & incoming & command(['auth']))
async def _auth(client, message):
    creds = db.get_credential(message.from_user.id)
    if creds is not None:
        try:
            creds.refresh(Http())
            db.set_credential(message.from_user.id, creds)
            await message.reply_text(
                "🔒 **Already authorized your Google Drive Account.**\n"
                "__Use /revoke to revoke the current account.__\n"
                "__Send me a direct link or File to Upload on Google Drive__",
                quote=True
            )
        except Exception as e:
            await message.reply_text(f"**ERROR (refresh):** ```{e}```", quote=True)
    else:
        try:
            flow = OAuth2WebServerFlow(
                G_DRIVE_CLIENT_ID,
                G_DRIVE_CLIENT_SECRET,
                OAUTH_SCOPE,
                redirect_uri=REDIRECT_URI
            )
            auth_url = flow.step1_get_authorize_url()
            user_flows[message.from_user.id] = flow
            await client.send_message(
                message.from_user.id,
                f"⛓️ **To Authorize your Google Drive account visit this [URL]({auth_url}) and send the generated code here.**\n"
                "__Visit the URL > Allow permissions > you will get a code. Send it here.__"
            )
        except Exception as e:
            await message.reply_text(f"**ERROR:** ```{e}```", quote=True)

@Client.on_message(private & incoming & command(['revoke']))
async def _revoke(client, message):
    if db.get_credential(message.from_user.id) is None:
        await message.reply_text(
            "🔑 **You have not authenticated me to upload to any account.**\n"
            "__Send /auth to authenticate.__", quote=True
        )
    else:
        try:
            db.clear_credential(message.from_user.id)
            await message.reply_text("🔓 **Authenticated Account revoked successfully.**", quote=True)
        except Exception as e:
            await message.reply_text(f"**ERROR:** ```{e}```", quote=True)

@Client.on_message(private & incoming & command(['setfolder']))
async def _set_parent(client, message):
    if len(message.command) > 1:
        cmd_msg = message.command[1]
        if cmd_msg.lower() == "clear":
            sql.del_id(message.from_user.id)
            await message.reply_text(
                '**Custom Folder ID Cleared**\n'
                '__Use /setfolder <Folder URL> to set it back.__',
                quote=True
            )
        else:
            file_id = getIdFromUrl(cmd_msg)
            if 'NotFound' in file_id:
                await message.reply_text(
                    '❗ **Invalid Folder URL**\n__Copy the custom folder id correctly.__',
                    quote=True
                )
            else:
                sql.set_id(message.from_user.id, file_id)
                await message.reply_text(
                    f'**Custom Folder ID set Successfully**\n'
                    f'__Your custom folder id set to {file_id}. All the uploads (from now) goes here.\n'
                    'Use__ ```/setfolder clear``` __to clear the folder.__', quote=True
                )
    else:
        parent = sql.get_id(message.from_user.id)
        if parent:
            await message.reply_text(
                f'**Your custom folder id is** ```{parent.parent_id}```.',
                quote=True
            )
        else:
            await message.reply_text(
                '**You did not set any Custom Folder ID**\n'
                '__Use__ ```/setfolder {folder URL}``` __to set your custom folder ID.__',
                quote=True
            )

@Client.on_message(private & incoming & text)
async def _token(client, message):
    token = message.text.strip()
    if len(token) == 57 and token[1] == "/":
        creds = None
        flow = user_flows.get(message.from_user.id)
        if flow is None:
            await message.reply_text(
                text="❗ **Invalid Code**\n__Run /auth first.__",
                quote=True
            )
            return
        try:
            m = await message.reply_text(text="**Checking received code...**", quote=True)
            creds = flow.step2_exchange(token)
            db.set_credential(message.from_user.id, creds)
            await m.edit('**Authorized Google Drive account Successfully.**')
            user_flows.pop(message.from_user.id, None)  # Remove used flow
        except FlowExchangeError:
            await m.edit(
                '❗ **Invalid Code**\n'
                '__The code you have sent is invalid or already used before. Generate a new one by the Authorization URL.__'
            )
        except Exception as e:
            await m.edit(f"**ERROR:** ```{e}```")

def getIdFromUrl(link: str):
    # Google Drive folder URL patterns
    found = re.search(
        r'https://drive\.google\.com/[\w\?\./&=]+([-\w]{33}|(?<=/)0A[-\w]{17})', link)
    if found:
        return found.group(1)
    elif len(link.split()[-1]) == 33 or len(link.split()[-1]) == 19:
        return link.split()[-1]
    else:
        return 'NotFound'
