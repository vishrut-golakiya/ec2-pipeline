from flask import Flask, render_template, request, redirect, url_for, session, flash
import redis, pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Redis cache
cache = redis.Redis(host='redis', port=6379)

# MySQL DB connection
def get_db():
    return pymysql.connect(
        host='mysql',
        user='root',
        password='rootpass',
        database='flaskdb',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password'], password):
                    session['user'] = email
                    return redirect(url_for('dashboard'))
        flash('Invalid login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
                if cursor.fetchone():
                    flash('User already exists')
                    return redirect(url_for('register'))
                hashed = generate_password_hash(password)
                cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed))
                conn.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
