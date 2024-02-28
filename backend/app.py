from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('website.db')
    conn.row_factory = sqlite3.Row
    return conn

# Создание таблицы для пользователей
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username VARCHAR(50) NOT NULL,
            Email VARCHAR(100) NOT NULL,
            Password VARCHAR(100) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Создание таблицы для заявок
def create_requests_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Requests (
            RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            RequestText TEXT,
            RequestDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES Users(UserID)
        )
    ''')
    conn.commit()
    conn.close()

# Функция для добавления нового пользователя в базу данных
def add_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Users (Username, Email, Password) 
        VALUES (?, ?, ?)
    ''', (username, email, password))
    conn.commit()
    conn.close()

# Функция для добавления новой заявки в базу данных
def add_request(user_id, request_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Requests (UserID, RequestText) 
        VALUES (?, ?)
    ''', (user_id, request_text))
    conn.commit()
    conn.close()

# Главная страница сайта - форма для отправки заявки
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        request_text = request.form['request_text']

        # Добавляем пользователя в базу данных (если его ещё нет)
        add_user(username, email, password)

        # Получаем UserID только что добавленного или уже существующего пользователя
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT UserID FROM Users WHERE Email = ?
        ''', (email,))
        user = cursor.fetchone()
        user_id = user['UserID']

        # Добавляем заявку в базу данных
        add_request(user_id, request_text)

        # Перенаправляем пользователя на страницу подтверждения
        return redirect(url_for('success'))

    return render_template('index.html')

# Страница подтверждения успешной отправки заявки
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    create_users_table()  # Создание таблицы пользователей при запуске приложения
    create_requests_table()  # Создание таблицы заявок при запуске приложения
    app.run(debug=True)
