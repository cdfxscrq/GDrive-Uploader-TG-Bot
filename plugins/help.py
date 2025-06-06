from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import Messages as tr


@Client.on_message(filters.private & filters.incoming & filters.command("start"))
async def _start(client: Client, message: Message):
    """Handle /start command in private messages."""
    await message.reply_text(
        text=tr.START_MSG.format(message.from_user.first_name),
        parse_mode="markdown",
        disable_notification=True,
        reply_to_message_id=message.id
    )


@Client.on_message(filters.private & filters.incoming & filters.command("help"))
async def _help(client: Client, message: Message):
    """Handle /help command in private messages."""
    await message.reply_text(
        text=tr.HELP_MSG[1],
        parse_mode="markdown",
        disable_notification=True,
        reply_markup=help_keyboard(1),
        reply_to_message_id=message.id
    )


def help_keyboard(pos: int) -> InlineKeyboardMarkup:
    """Return an InlineKeyboardMarkup for help navigation."""
    if pos == 1:
        buttons = [
            [InlineKeyboardButton(text="-->", callback_data="help+2")]
        ]
    elif pos == len(tr.HELP_MSG) - 1:
        buttons = [
            [InlineKeyboardButton(text="Support Chat", url="https://www.github.com/cdfxscrq")],
            [InlineKeyboardButton(text="Feature Request", url="https://t.me/Akshayan1")],
            [InlineKeyboardButton(text="<--", callback_data=f"help+{pos-1}")]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="<--", callback_data=f"help+{pos-1}"),
                InlineKeyboardButton(text="-->", callback_data=f"help+{pos+1}")
            ]
        ]
    return InlineKeyboardMarkup(buttons)


@Client.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("help+")))
async def help_answer(client: Client, callback_query: CallbackQuery):
    """Handle help navigation via inline buttons."""
    try:
        pos = int(callback_query.data.split("+")[1])
        await callback_query.answer()  # Remove the "loading" animation
        await callback_query.edit_message_text(
            text=tr.HELP_MSG[pos],
            parse_mode="markdown",
            reply_markup=help_keyboard(pos)
        )
    except (IndexError, ValueError, KeyError):
        await callback_query.answer("Invalid help page.", show_alert=True)
