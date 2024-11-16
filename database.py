import sqlite3

DATABASE_PATH = 'users.db'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    return conn

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Создание таблицы users с дополнительным столбцом referrer_id и invites
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        referrer_id INTEGER,
        invites INTEGER DEFAULT 0,
        FOREIGN KEY(referrer_id) REFERENCES users(user_id) ON DELETE SET NULL
    )
    ''')

    # Таблица referrals для хранения рефералов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        user_id INTEGER,
        referral_id INTEGER,
        UNIQUE(user_id, referral_id)
    )
    ''')

    conn.commit()
    conn.close()  # Закрываем соединение после создания базы

# Добавление пользователя с referrer_id
def add_user(user_id, balance=0, referrer_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Добавление пользователя в таблицу users, включая referrer_id
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance, referrer_id) VALUES (?, ?, ?)', 
                   (user_id, balance, referrer_id))
    conn.commit()
    conn.close()

# Получение информации о пользователе
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    # Если пользователь найден, возвращаем словарь с данными
    if user:
        return {
            'user_id': user[0],
            'balance': user[1],
            'invites': user[2],
            'is_banned': user[3]  # Столбец с статусом блокировки
        }
    return None


# Обновление баланса пользователя
def update_user(user_id, new_balance):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

# Получение топ пользователей с наибольшим балансом
def get_top_users(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT ?', (limit,))
    top_users = cursor.fetchall()
    conn.close()
    return [{'user_id': row[0], 'balance': row[1]} for row in top_users]

# Функция для добавления нового реферала
def add_referral(user_id, referral_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Добавляем реферала в таблицу referrals
    cursor.execute('INSERT OR IGNORE INTO referrals (user_id, referral_id) VALUES (?, ?)', 
                   (user_id, referral_id))

    # Увеличиваем счетчик приглашений у пригласившего пользователя
    cursor.execute('UPDATE users SET invites = invites + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# Получение списка рефералов для пользователя
def get_referrals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT referral_id FROM referrals WHERE user_id = ?', (user_id,))
    referrals = cursor.fetchall()
    conn.close()
    return [referral[0] for referral in referrals]

# Получение количества приглашений для пользователя
def get_invites_count(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем количество рефералов для данного пользователя
    cursor.execute('SELECT COUNT(*) FROM referrals WHERE user_id = ?', (user_id,))
    invites_count = cursor.fetchone()[0]  # Извлекаем количество
    conn.close()

    return invites_count

def add_is_banned_column():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0')
        conn.commit()
    except sqlite3.OperationalError:
        # Столбец уже существует, ничего не делаем
        pass
    conn.close()


# Инициализация базы данных при запуске
init_db()
