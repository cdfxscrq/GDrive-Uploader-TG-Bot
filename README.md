# Google Drive Uploader Telegram Bot
**An asyncio Telegram bot to upload files from Telegram or Direct links to Google Drive.**
**一个异步电报机器人，用于从电报或直接链接上传文件到Google云端硬盘。**

- Find it on Telegram as [Google Drive Uploader](https://t.me/uploadgdrivebot)

## Features
- [X] Telegram files support -- 电报文件支持
- [X] Direct Links support -- 直链支持
- [X] Custom Upload Folder -- 自定义上传文件夹
- [X] TeamDrive Support -- 支持团队盘
- [X] Clone/Copy Google Drive Files -- 克隆/复制Google云端硬盘文件

## ToDo 
- [ ] Handle more exceptions -- 处理更多异常
- [ ] LOGGER support -- 记录仪支持
- [ ] Service account support -- 服务帐户支持

## Deploying

### Installation
- Clone this git repository.
```sh 
git clone https://github.com/viperadnan-git/gdrive-uploader-telegram-bot
```
- Change Directory
```sh 
cd gdrive-uploader-telegram-bot
```
- Install requirements with pip3
```sh 
pip3 install -r requirements.txt
```

### Configuration
**There are two Ways for configuring this bot.**
**有两种配置此漫游器的方法。**
- Add [APP_ID](https://my.telegram.org/apps), [API_HASH](https://my.telegram.org/apps), [BOT_TOKEN](https://t.me/BotFather), DATABASE_URL, ENV in Environment Variables.
- Add [APP_ID](https://my.telegram.org/apps), [API_HASH](https://my.telegram.org/apps), [BOT_TOKEN](https://t.me/BotFather), DATABASE_URL in [config.py](./config.py)

## Deploy 
- Deploy on VPS.
```sh 
python3 bot.py
```
## Deploy on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/cdfxscrq/gdrive-uploader-telegram-bot/tree/master)

- Note: Bot is in beta stage. Maybe it throw some errors. 
- 注意：Bot处于测试阶段。也许会引发一些错误。

## Credits
- [Dan](https://github.com/delivrance) for [PyroGram](https://pyrogram.org)
- [Spechide](https://github.com/Spechide) for [gDrive_sql.py](./helpers/gDrive_sql.py)
- [Shivam Jha](https://github.com/lzzy12) for [python-aria-mirror-bot](https://github.com/lzzy12/python-aria-mirror-bot)
