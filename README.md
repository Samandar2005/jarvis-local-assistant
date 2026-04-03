# Jarvis Local Assistant

Bu loyiha kompyuter bilan ishlash, kod yozish va oddiy desktop avtomatlashtirish uchun lokal AI yordamchi skeletidir.

## Nima qila oladi

- web interfeys orqali chat
- brauzer ochish
- `notepad`, `calculator`, `explorer` kabi ilovalarni ishga tushirish
- workspace ichida fayl yaratish
- faylni o'qish
- Python skriptini ishga tushirish
- `OPENAI_API_KEY` ulangan bo'lsa, erkin AI chat va kod bo'yicha javoblar
- brauzer qo'llasa, voice input va text-to-speech

## Tuzilma

```text
app/
  main.py
  config.py
  schemas.py
  services/
    assistant_service.py
    command_router.py
    llm_service.py
    system_actions.py
static/
  index.html
  styles.css
  app.js
requirements.txt
```

## Ishga tushirish

1. Virtual environment yarating:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Kutubxonalarni o'rnating:

```powershell
pip install -r requirements.txt
```

3. `.env.example` dan `.env` yarating va kerak bo'lsa API kalit kiriting:

```powershell
Copy-Item .env.example .env
```

4. Serverni ishga tushiring:

```powershell
uvicorn app.main:app --reload
```

5. Brauzerda oching:

```text
http://127.0.0.1:8000
```

## Foydalanish misollari

- `brauzerni och va youtube.com saytiga kir`
- `create file hello.py with content print('salom')`
- `read file hello.py`
- `run python script hello.py`
- `nima qila olasan`

## Keyingi kengaytirish g'oyalari

- Telegram bot ulash
- Whisper bilan aniqroq speech-to-text
- foydalanuvchidan tasdiq so'raydigan xavfsiz action queue
- ko'proq tool: screenshot, clipboard, process manager, reminders
- OpenAI function calling yoki agent loop qo'shish
