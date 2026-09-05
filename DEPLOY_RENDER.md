# MusRemixBot: Render + UptimeRobot

## 1. Render
Create a Docker Web Service from this repository, or use `render.yaml`.

Add these secrets in Render Environment:
- BOT_TOKEN
- ADMIN_ID
- VK_TOKEN
- YANDEX_SPEECH_KEY (only if used)
- GOOGLE_SPEECH_KEY (only if used)

Do NOT commit `.env` or real tokens to GitHub.

The bot itself is still started from the original `main.py`.
`run_render.py` is only a deployment wrapper that exposes `/health` and
stops the container if the original bot process exits.

## 2. Render health URL
After deployment, Render gives the service a public HTTPS address:

`https://YOUR-SERVICE.onrender.com/health`

It should return HTTP 200 while the bot process is alive.

## 3. UptimeRobot
Create an HTTP(s) monitor:
- URL: `https://YOUR-SERVICE.onrender.com/health`
- Monitoring interval: 5 minutes (or the lowest interval available to your plan)
- Expected status: HTTP 200

This keeps the Render web service receiving traffic and gives you an external
health check.

## Important
Never place BOT_TOKEN, VK_TOKEN, or other secret keys in GitHub files.
Store them only in Render Environment Variables.
