from pyrogram import Client
from config import Config

# Plugins directory
plugins = dict(root="plugins")

def main():
    try:
        app = Client(
            "GDrive-Uploader-TG-Bot",
            bot_token=Config.BOT_TOKEN,
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            plugins=plugins
        )
        app.run()
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
