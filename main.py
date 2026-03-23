import re
from message_cut import message_cut
from _time import approx_tokens_for_text, ensure_today_bucket, add_used_today, get_resp_total_tokens, get_used_today
from init import init
from main_messages_and_promts import (greet_message, unauthorized_message,
                                      system_prompt, new_dialog,risky_system_prompt)

BOT_TOKEN, OPENAI_TOKEN, bot, client, users, risky, MAX_TOKENS_PER_DAY, model = init()

# print(users)




# ----------- ДНЕВНОЙ ЛИМИТ ТОКЕНОВ -----------

user_daily_tokens = {}
user_history = {}
reasoning = 'low'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, greet_message)

@bot.message_handler(commands=['dialog'])
def dialog(message):
    # print(message.chat.id, users)
    if message.chat.id not in users:
        bot.send_message(message.chat.id, unauthorized_message)
        return
    user_history[message.chat.id] = [
        system_prompt
    ]
    if message.chat.id in risky:
        user_history[message.chat.id] = [
            {risky_system_prompt}
        ]
    bot.send_message(
        message.chat.id,
        f"Начало нового диалога с нейросетью. Выберите reasoning и наслаждайтесь диалогом! reasoning is {reasoning}. "
        f"Change: /low /medium /high\n"
        f"Дневной лимит токенов (UTC): {MAX_TOKENS_PER_DAY}. Посмотреть расход: /tokens"
    )
    bot.register_next_step_handler(message, prompt)


def stop(message):
    user_history[message.chat.id] = []
    bot.send_message(message.chat.id, new_dialog)


def prompt(message):
    global reasoning

    uid = message.chat.id
    if message.text.startswith('/'):
        q = message.text
        if q == '/stop':
            stop(message)
            return
        elif q == '/low':
            reasoning = 'low'
            bot.send_message(uid, f'reasoning is {reasoning}')
        elif q == '/medium':
            reasoning = 'medium'
            bot.send_message(uid, f'reasoning is {reasoning}')
        elif q == '/high':
            reasoning = 'high'
            bot.send_message(uid, f'reasoning is {reasoning}')
        elif q == '/tokens':
            bucket = ensure_today_bucket(uid, user_daily_tokens)
            used = bucket['used']
            remain = max(0, MAX_TOKENS_PER_DAY - used)
            bot.send_message(
                uid,
                f"Сегодня (UTC: {bucket['date']}) израсходовано токенов: {used} из {MAX_TOKENS_PER_DAY}. "
                f"Осталось: {remain}. Лимит сбросится в 00:00 UTC."
            )
        else:
            bot.send_message(uid, "Неизвестная команда.")
        bot.register_next_step_handler(message, prompt)
        return

    used = get_used_today(uid, user_daily_tokens)
    if used >= MAX_TOKENS_PER_DAY:
        bucket = ensure_today_bucket(uid, user_daily_tokens)
        bot.send_message(
            uid,
            f"Дневной лимит токенов (UTC) исчерпан: {used} из {MAX_TOKENS_PER_DAY}. "
            f"Дата (UTC): {bucket['date']}. Лимит сбросится в 00:00 UTC."
        )
        bot.register_next_step_handler(message, prompt)
        return

    user_history.setdefault(uid, [])
    user_history[uid].append({"role": "user", "content": message.text})
    try:
        response = client.chat.completions.create(
            model=model,
            reasoning_effort = reasoning,
            messages=user_history[uid]
        )
        textofresponse = response.choices[0].message.content
        user_history[uid].append({"role": "assistant", "content": textofresponse})

        delta_tokens = get_resp_total_tokens(response)
        if delta_tokens is None:
            delta_tokens = approx_tokens_for_text(message.text) + approx_tokens_for_text(textofresponse)

        used_now = add_used_today(uid, int(delta_tokens), user_daily_tokens)
        remain = MAX_TOKENS_PER_DAY - used_now
        if remain <= 0:
            bot.send_message(uid, f"Достигнут дневной лимит {MAX_TOKENS_PER_DAY} токенов. Следующие сообщения сегодня не будут обрабатываться.")

        cd = [match.start() for match in re.finditer('```', textofresponse)]
        message_cut(textofresponse, message, bot)
    except Exception as e:
        bot.send_message(uid, f"Произошла ошибка: {e}")

    bot.register_next_step_handler(message, prompt)


bot.polling(none_stop=True)