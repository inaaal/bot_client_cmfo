import requests
import urllib3
from flask import Flask, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

BOT_TOKEN   = '8739969583:AAElf56svjZmlHbj-ZfaSaasHS_7qZQcTmU'
WEBHOOK_URL = 'https://ВАШ-СЕРВИС.onrender.com/webhook'   
API_URL     = 'https://cryptomfo.hhos.net/api/bot.php'
API_SECRET  = 'inaaal'

def tg(method, **payload):
    try:
        return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
                             json=payload, timeout=30).json()
    except Exception as e:
        print('tg error:', e); return None

def api_request(action, chat_id=0, data=None):
    payload = {'action': action, 'chat_id': chat_id}
    if data:
        payload.update(data)
    try:
        r = requests.post(API_URL, json=payload, timeout=60,
                          headers={'X-Bot-Secret': API_SECRET,
                                   'Content-Type': 'application/json'},
                          verify=False)
        return r.json()
    except Exception as e:
        print('api error:', repr(e)); return {}

def send(chat_id, text, parse_mode='Markdown'):
    return tg('sendMessage', chat_id=chat_id, text=text,
              parse_mode=parse_mode, disable_web_page_preview=True)

def handle_message(msg):
    chat_id = msg['chat']['id']
    text = (msg.get('text') or '').strip()

    if text == '/start':
        result = api_request('check_binding', chat_id)
        if result.get('success'):
            user = result['user']
            send(chat_id,
                 f"✅ *Telegram успешно привязан!*\n\n"
                 f"👤 Аккаунт: {user['email']}\n"
                 f"💰 Баланс: ${user['balance']:.2f}")
        else:
            send(chat_id,
                 "👋 Добро пожаловать в Crypto MFO!\n\n"
                 "🔑 Введите код, который вы получили на сайте для привязки Telegram аккаунта.\n\n"
                 "📋 Код состоит из 6 цифр и действует 5 минут.")
        return

    # Любой другой текст — трактуем как код
    code = text
    if not code.isdigit() or len(code) != 6:
        send(chat_id,
             "❌ Код должен состоять из 6 цифр.\n"
             "Пожалуйста, введите код правильно.")
        return

    result = api_request('verify_code', chat_id, {'code': code})
    if result.get('success'):
        send(chat_id,
             f"✅ {result['message']}\n\n"
             f"Теперь вы можете войти на сайт без пароля!")
    else:
        send(chat_id,
             f"❌ {result.get('message', 'Ошибка')}\n\n"
             "Проверьте код и попробуйте еще раз.")

@app.route('/webhook', methods=['POST'])
def webhook():
    u = request.get_json(force=True, silent=True) or {}
    if 'message' in u:
        try: handle_message(u['message'])
        except Exception as e: print('msg err', e)
    return 'OK', 200

@app.route('/set_webhook')
def set_webhook():
    return jsonify(requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        params={'url': WEBHOOK_URL}, timeout=15).json())

@app.route('/webhook_info')
def webhook_info():
    return jsonify(requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo",
        timeout=15).json())

@app.route('/health')
def health(): return 'OK', 200

@app.route('/')
def home(): return 'CLIENTS bot', 200

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
