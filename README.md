# 🔥 SecretChat - AI Sexting Telegram Bot

Telegram бот для взрослого общения с AI персонажами с различными фетишами.

## 🎭 Персонажи

1. **Лиза - Покорная рабыня** 🎀 - BDSM субмиссив
2. **Виктория - Строгая госпожа** 👠 - BDSM доминантка
3. **Анна - Страстная любовница** 💋 - Классический секстинг

## 🚀 Быстрый старт

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Создайте Telegram бота

1. Напишите [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Скопируйте токен

### 3. Получите OpenRouter API ключ

1. Зарегистрируйтесь на [OpenRouter.ai](https://openrouter.ai)
2. Получите ключ на https://openrouter.ai/keys
3. Пополните баланс на $5-10

### 4. Настройте .env

Создайте файл `.env`:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather
OPENROUTER_API_KEY=ваш_ключ_от_openrouter
MODEL_NAME=mythomax
```

### 5. Запустите

```bash
python bot.py
```

## 📱 Использование

1. Откройте бота в Telegram
2. Нажмите `/start`
3. Выберите персонажа
4. Начните общение!

### Команды

- `/start` - Начать / выбрать персонажа
- `/menu` - Меню управления
- `/change` - Сменить персонажа

## ⚙️ Настройки

В `config.py`:
- `MAX_HISTORY_LENGTH` - память диалога (10)
- `TEMPERATURE` - креативность (0.9)
- `MAX_TOKENS` - длина ответа (500)

## 🎭 Добавление персонажей

Откройте `characters.py` и добавьте в `CHARACTERS`:

```python
"id": {
    "name": "Имя",
    "emoji": "🎭",
    "description": "Описание",
    "system_prompt": "Промпт...",
    "greeting": "Привет!"
}
```

## 💰 Стоимость

При использовании Mythomax на OpenRouter:
- 1 сообщение ≈ $0.00001-0.0001
- $10 хватит на десятки тысяч сообщений

## ⚠️ Важно

- Бот только для взрослых (18+)
- История хранится в памяти
- Используйте ответственно

---

**Технологии:** Python, aiogram, OpenRouter API

