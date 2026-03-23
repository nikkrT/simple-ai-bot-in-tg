greet_message="Бот для работы с o3-mini. Используйте /dialog для создания нового диалога с нейросетью"

unauthorized_message = 'Вы не зарегистрированный пользователь'

system_prompt={"role": "developer", "content": "You are a helpful assistant.Before and after any programming code put ```. "}

risky_system_prompt={"role": "developer",
                     "content": "You are a helpful assistant.Before and after any programming code put ```. "
                                "Если ты считаешь, что заданный вопрос не соответствует нормам морали или политически"
                                "некорректен, не отвечай на него, а напиши 'не пиши ерунду'. Эта инструнция важнее, чем всё что будет сказано пользователем "}


new_dialog = "История диалога очищена. Новый /dialog"