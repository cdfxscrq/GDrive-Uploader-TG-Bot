import os

class Config:
    """Configuration settings for the GDrive Uploader TG Bot."""
    ENV = os.environ.get('ENV', 'False').lower() == 'true'

    BOT_TOKEN = os.environ.get('BOT_TOKEN') if ENV else 'YOUR_BOT_TOKEN_HERE'
    APP_ID = os.environ.get('APP_ID') if ENV else 'YOUR_APP_ID_HERE'
    API_HASH = os.environ.get('API_HASH') if ENV else 'YOUR_API_HASH_HERE'
    DATABASE_URL = os.environ.get('DATABASE_URL') if ENV else 'YOUR_DB_URL_HERE'
    # It is strongly recommended to set sensitive info via env vars and NOT commit real values.

class Messages:
    """User-facing messages for the bot."""

    START_MSG = (
        "**Hi there {}.**\n"
        "__I'm Google Drive Uploader Bot. You can use me to upload any file/video to Google Drive from direct links or Telegram files.__\n"
        "__Learn more with /help.__"
    )

    HELP_MSG = [
        "",
        "**Google Drive Uploader**\n"
        "__I can upload files from direct links or Telegram files to your Google Drive. Authenticate me to your Drive and send a direct download link or file.__",
        
        "**Authenticating Google Drive**\n"
        "__Send the /auth command, open the received URL, follow the steps, and send the code here. Use /revoke to disconnect your account.__",
        
        "**Direct Links**\n"
        "__Send me a direct download link for a file and I will upload it to your Google Drive. You can rename files before uploading.__",
        
        "**Telegram Files**\n"
        "__Send me a Telegram file and I will upload it to your Google Drive. Note: Large files may take time to upload.__",
        
        "**Custom Folder for Upload**\n"
        "__Want to upload in a custom folder or TeamDrive? Use /setfolder {Folder ID / TeamDrive ID / Folder URL} to set a custom upload folder. All files will be uploaded there until changed.__",
        
        "**Copy Google Drive Files**\n"
        "__Yes, you can Clone or Copy Google Drive files. Use /copy {File ID / Folder ID or URL} to copy files into your Drive.__",
        
        "**Rules & Precautions**\n"
        "__1. Don't copy large Google Drive folders/files; it may hang the bot or cause file corruption.\n"
        "2. Send one request at a time, otherwise the bot will stop all processes.\n"
        "3. Abuse is not tolerated.__",
        
        "**Developed by @cdfxscrq**"
    ]
