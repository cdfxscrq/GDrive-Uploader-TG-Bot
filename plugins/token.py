import re
from httplib2 import Http
from pyrogram import Client, Filters
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from helpers import gDrive_sql as db
from helpers import parent_id_sql as sql

OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
G_DRIVE_CLIENT_ID = "197036948433-4sjgjrj1osm5b5neu8khh7c2nsvn96f7.apps.googleusercontent.com"
G_DRIVE_CLIENT_SECRET = "dnXoMIu2V7HQ8G8RicrKmvlu"
flow = None

@Client.on_message(Filters.private & Filters.incoming & Filters.command(['auth']))
async def _auth(client, message):
  creds = db.get_credential(message.from_user.id)
  if creds is not None:
    creds.refresh(Http())
    db.set_credential(message.from_user.id, creds)
    await message.reply_text("🔒 **Already authorized your Google Drive Account.**\n__Use /revoke to revoke the current account.__\n__Send me a direct link or File to Upload on Google Drive__", quote=True)
  else:
    global flow
    try:
      flow = OAuth2WebServerFlow(
              G_DRIVE_CLIENT_ID,
              G_DRIVE_CLIENT_SECRET,
              OAUTH_SCOPE,
              redirect_uri=REDIRECT_URI
      )
      auth_url = flow.step1_get_authorize_url()
      await client.send_message(message.from_user.id, "⛓️ **To Authorize your Google Drive account visit this [URL]({}) and send the generated code here.**\n__Visit the URL > Allow permissions > you will get a code > copy it > Send it here__".format(auth_url))
    except Exception as e:
      await message.reply_text(f"**ERROR:** ```{e}```", quote=True)


@Client.on_message(Filters.private & Filters.incoming & Filters.command(['revoke']))
async def _revoke(client, message):
  if db.get_credential(message.from_user.id) is None:
   await message.reply_text("🔑 **You have not authenticated me to upload to any account.**\n__Send /auth to authenticate.__", quote=True)
  else:
    try:
      db.clear_credential(message.from_user.id)
      await message.reply_text("🔓 **Authenticated Account revoked successfully.**", quote=True)
    except Exception as e:
      await message.reply_text(f"**ERROR:** ```{e}```", quote=True)


@Client.on_message(Filters.private & Filters.incoming & Filters.command(['setfolder']))
async def _set_parent(client, message):
  if len(message.command) > 1:
    cmd_msg = message.command[1]
    if cmd_msg.lower() == "clear":
      sql.del_id(message.from_user.id)
      await message.reply_text('**Custom Folder ID Cleared**\n__Use /setfolder <Folder URL> to set it back.__', quote=True)
    else:
      file_id = getIdFromUrl(cmd_msg)
      if 'NotFound' in file_id:
        await message.reply_text('❗ Invalid Folder URL**\n__Copy the custom folder id correctly.__', quote=True)
      else:
        sql.set_id(message.from_user.id, file_id)
        await message.reply_text(f'**Custom Folder ID sets Successfully**\n__Your custom folder id set to {file_id}. All the uploads (from now) goes here.\nUse__ ```/setfolder clear``` __to clear the current Folder ID.__', quote=True)
  else:
    if sql.get_id(message.from_user.id):
      await message.reply_text(f'**Your custom folder id is** ```{sql.get_id(message.from_user.id).parent_id}```.', quote=True)
    else:
      await message.reply_text('**You did not set any Custom Folder ID**\n__Use__ ```/setfolder {folder URL}``` __to set your custom folder ID.__', quote=True)

@Client.on_message(Filters.private & Filters.incoming & Filters.text)
async def _token(client, message):
  token = message.text.split()[-1]
  WORD = len(token)
  if WORD == 57 and token[1] == "/":
    creds = None
    global flow
    if flow is None:
        await message.reply_text(
            text="❗ **Invalid Code**\n__Run /auth first.__",
            quote=True
        )
        return
    try:
      m = await message.reply_text(text="**Checking received code...**", quote=True)
      creds = flow.step2_exchange(message.text)
      db.set_credential(message.from_user.id, creds)
      await m.edit('**Authorized Google Drive account Successfully.**')
      flow = None
    except FlowExchangeError:
      await m.edit('❗ **Invalid Code**\n__The code you have sent is invalid or already used before. Generate new one by the Authorization URl__')
    except Exception as e:
      await m.edit(f"**ERROR:** ```{e}```")


def getIdFromUrl(link: str):
      found = re.search(
        r'https://drive.google.com/[\w\?\./&=]+([-\w]{33}|(?<=/)0A[-\w]{17})', link)
      if found:
        return found.group(1)
      elif len(link.split()[-1]) == 33 or len(link.split()[-1]) == 19:
        return link
      else:
        return 'NotFound'