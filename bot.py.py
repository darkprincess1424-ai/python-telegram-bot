import json
import urllib.request
import urllib.parse
import time
from datetime import datetime
import os

# === КОНФИГУРАЦИЯ ===
TOKEN = "8253975192:AAGA10BP7WQZtiBy10aBICmccz20OXux7cw"
ADMIN_ID = 8281804228

# === БАЗЫ ДАННЫХ ===
scammers_db = {}   # username: {'count': int, 'proofs': str, 'date': str}
garants_db = {}    # username: {'info': str, 'date': str}
search_stats = {}  # username: count
user_ratings = {}  # username: {'likes': int, 'dislikes': int}

# === СОХРАНЕНИЕ ДАННЫХ ===
def save_data():
    """Сохранить все данные в файл"""
    data = {
        'scammers': scammers_db,
        'garants': garants_db,
        'searches': search_stats,
        'ratings': user_ratings
    }
    try:
        with open('antiscam_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 Данные сохранены")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def load_data():
    """Загрузить данные из файла"""
    global scammers_db, garants_db, search_stats, user_ratings
    try:
        if os.path.exists('antiscam_data.json'):
            with open('antiscam_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                scammers_db = data.get('scammers', {})
                garants_db = data.get('garants', {})
                search_stats = data.get('searches', {})
                user_ratings = data.get('ratings', {})
            print(f"📂 Данные загружены: {len(scammers_db)} скамеров, {len(garants_db)} гарантов")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки: {e}")

# === КЛАСС БОТА ===
class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, chat_id, text, buttons=None):
        """Отправить сообщение с кнопками"""
        url = f"{self.base_url}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if buttons:
            data['reply_markup'] = json.dumps({'inline_keyboard': buttons})
        
        try:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, 
                                      headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"⚠️ Ошибка отправки: {e}")
            return None
    
    def get_updates(self, offset=None, timeout=30):
        """Получить обновления от Telegram"""
        url = f"{self.base_url}/getUpdates?timeout={timeout}"
        if offset:
            url += f"&offset={offset}"
        
        try:
            with urllib.request.urlopen(url, timeout=35) as response:
                return json.loads(response.read().decode())
        except Exception:
            return {'ok': False, 'result': []}
    
    def answer_callback(self, callback_id):
        """Ответить на нажатие кнопки"""
        url = f"{self.base_url}/answerCallbackQuery"
        data = {'callback_query_id': callback_id}
        
        try:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, 
                                      headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10):
                return True
        except Exception:
            return False

# === СОЗДАЕМ БОТА ===
bot = TelegramBot(TOKEN)

# === ОСНОВНЫЕ ФУНКЦИИ ===
def start_command(chat_id, user_id, username):
    """Обработка команды /start"""
    text = (
        "Добро Пожаловать в 𝐀𝐧𝐭𝐢 𝐬𝐜𝐚𝐦 [🔍]\n\n"
        "Если вас обманули, вы можете слить скамера в предложку 🕵️\n\n"
        "⚡️ Возможности:\n"
        "• /check @username - проверка пользователя\n"
        "• /check в ответ на сообщение - проверка отправителя\n"
        "• /me - проверить себя\n"
        "• База для слива скамеров"
    )
    
    buttons = [
        [
            {"text": "👤 Мой профиль", "callback_data": "my_profile"},
            {"text": "📋 Гаранты", "callback_data": "garants"}
        ],
        [
            {"text": "⚠️ Слить скамера", "url": "https://t.me/antiscambaseAS"},
            {"text": "📢 Новости", "url": "https://t.me/AntiScamLaboratory"}
        ],
        [
            {"text": "👍", "callback_data": "like"},
            {"text": "👎", "callback_data": "dislike"}
        ]
    ]
    
    bot.send_message(chat_id, text, buttons)

def check_user(chat_id, username):
    """Проверить пользователя"""
    if not username or username == "None":
        bot.send_message(chat_id, "❌ У пользователя нет username")
        return
    
    # Статистика поисков
    search_stats[username] = search_stats.get(username, 0) + 1
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    if username in scammers_db:
        scam = scammers_db[username]
        text = (
            f"👤 User: @{username}\n"
            f"🤖 Идет проверка в базе...\n"
            f"📍 СКАМЕР\n"
            f"Количество скамов: {scam.get('count', 1)}\n\n"
            f"Пруфы на скам ⏬\n"
            f"{scam.get('proofs', 'Нет пруфов')}\n\n"
            f"👁‍🗨 Пользователя искали: {search_stats[username]} раз\n"
            f"🔝 Проверенно @AntilScam_Bot\n\n"
            f"🗓️ Дата и время проверки [{current_time}]\n\n"
            f"От администрации: прошу не вестись на скам 💕"
        )
    elif username in garants_db:
        garant = garants_db[username]
        text = (
            f"👤 User: @{username}\n"
            f"🤖 Идет проверка в базе...\n"
            f"✅ ГАРАНТ\n"
            f"Информация: {garant.get('info', 'Проверенный гарант')}\n\n"
            f"👁‍🗨 Пользователя искали: {search_stats.get(username, 0)} раз\n"
            f"🔝 Проверенно @AntilScam_Bot\n\n"
            f"🗓️ Дата и время проверки [{current_time}]\n\n"
            f"От администрации: прошу не вестись на скам 💕"
        )
    else:
        text = (
            f"👤 User: @{username}\n"
            f"🤖 Идет проверка в базе...\n"
            f"🗯 Пользователя нету в базе данных.\n\n"
            f"👁‍🗨 Пользователя искали: {search_stats.get(username, 0)} раз\n"
            f"🔝 Проверенно @AntilScam_Bot\n\n"
            f"🗓️ Дата и время проверки [{current_time}]\n\n"
            f"От администрации: прошу не вестись на скам 💕"
        )
    
    buttons = [
        [
            {"text": "👍", "callback_data": f"like_{username}"},
            {"text": "👎", "callback_data": f"dislike_{username}"},
            {"text": "⚠️ Слить", "url": "https://t.me/antiscambaseAS"}
        ]
    ]
    
    bot.send_message(chat_id, text, buttons)
    save_data()

# === ОБРАБОТКА КОМАНД АДМИНА ===
def admin_command(user_id, chat_id, text):
    """Обработка админ команд"""
    if user_id != ADMIN_ID:
        bot.send_message(chat_id, "❌ Нет прав")
        return
    
    parts = text.split()
    
    if text.startswith('/add ') and len(parts) > 1:
        username = parts[1].lstrip('@')
        proof = " ".join(parts[2:]) or "Нет пруфов"
        
        if username in scammers_db:
            scammers_db[username]['count'] += 1
            scammers_db[username]['proofs'] += f"\n{proof}"
        else:
            scammers_db[username] = {
                'count': 1,
                'proofs': proof,
                'date': datetime.now().strftime("%d.%m.%Y")
            }
        
        bot.send_message(chat_id, f"✅ @{username} добавлен как скамер")
        save_data()
    
    elif text.startswith('/add_garant ') and len(parts) > 1:
        username = parts[1].lstrip('@')
        info = " ".join(parts[2:]) or "Проверенный гарант"
        
        garants_db[username] = {
            'info': info,
            'date': datetime.now().strftime("%d.%m.%Y")
        }
        
        bot.send_message(chat_id, f"✅ @{username} добавлен как гарант")
        save_data()

# === ГЛАВНЫЙ ЦИКЛ БОТА ===
def main():
    """Запуск бота"""
    load_data()
    
    print("=" * 50)
    print("🤖 Бот Anti Scam запущен!")
    print(f"👑 Админ: {ADMIN_ID}")
    print(f"📊 Скамеров: {len(scammers_db)} | Гарантов: {len(garants_db)}")
    print("=" * 50)
    
    offset = 0
    
    while True:
        try:
            # Получаем сообщения
            updates = bot.get_updates(offset)
            
            if updates.get('ok'):
                for update in updates['result']:
                    offset = update['update_id'] + 1
                    
                    # Текстовое сообщение
                    if 'message' in update:
                        msg = update['message']
                        chat_id = msg['chat']['id']
                        user_id = msg['from']['id']
                        username = msg['from'].get('username', '')
                        
                        if 'text' in msg:
                            text = msg['text']
                            
                            if text == '/start':
                                start_command(chat_id, user_id, username)
                            
                            elif text == '/me':
                                check_user(chat_id, username)
                            
                            elif text.startswith('/check'):
                                parts = text.split()
                                if len(parts) > 1:
                                    check_user(chat_id, parts[1].lstrip('@'))
                                else:
                                    bot.send_message(chat_id, "Используйте: /check @username")
                            
                            # Админ команды
                            elif text.startswith('/add'):
                                admin_command(user_id, chat_id, text)
                    
                    # Нажатие кнопки
                    elif 'callback_query' in update:
                        callback = update['callback_query']
                        bot.answer_callback(callback['id'])
                        
                        data = callback['data']
                        chat_id = callback['message']['chat']['id']
                        user_id = callback['from']['id']
                        username = callback['from'].get('username', '')
                        
                        if data == 'my_profile':
                            profile_text = f"👤 Профиль\nUsername: @{username}\nID: {user_id}"
                            bot.send_message(chat_id, profile_text)
                        
                        elif data == 'garants':
                            if garants_db:
                                text = "📋 Гаранты:\n\n" + "\n".join([f"• @{user}" for user in garants_db])
                            else:
                                text = "Список гарантов пуст"
                            bot.send_message(chat_id, text)
                        
                        elif data.startswith('like_'):
                            user = data.replace('like_', '')
                            bot.send_message(chat_id, f"👍 Вы оценили @{user}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)

# === ЗАПУСК ===
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
        save_data()