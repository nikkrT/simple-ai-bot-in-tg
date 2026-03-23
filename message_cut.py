from telebot import util
def escape_markdown(text):
    to_escape = r"_*[]()~`>#+-=|{}.! "
    return ''.join(['\\' + c if c in to_escape else c for c in text])

def message_cut(text, message, bot):
    parts = text.split("```")

    for i, part in enumerate(parts):
        if not part.strip():
            continue

        if i % 2 == 1:
            chunks = util.smart_split(part, chars_per_string=4080)
            for chunk in chunks:
                if chunk.strip():
                    code_msg = f"```{chunk}```"
                    try:
                        bot.send_message(message.chat.id, code_msg, parse_mode="MarkdownV2")
                    except Exception as e:
                        print(f"Markdown error: {e}")
                        bot.send_message(message.chat.id, chunk)

        else:
            chunks = util.smart_split(part, chars_per_string=4096)
            for chunk in chunks:
                if chunk.strip():
                    bot.send_message(message.chat.id, chunk)

    bot.send_message(message.chat.id, "/stop dialog?")