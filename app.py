from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# ✅ Secret key loaded from Render environment
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_key')

# Dummy admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS contact (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    mobile TEXT,
                    message TEXT)''')
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        message = request.form['message']

        # Debug log to check if data is received
        print(f"[CONTACT FORM] Received: {name}, {email}, {mobile}, {message}")

        # Save to SQLite
        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO contact (name, email, mobile, message) VALUES (?, ?, ?, ?)",
                     (name, email, mobile, message))
        conn.commit()
        conn.close()

        # Save to Excel (Render allows only /tmp directory for writing)
        excel_file = 'contacts.xlsx'
        data = {
            "Name": [name],
            "Email": [email],
            "Mobile": [mobile],
            "Message": [message]
        }
        df = pd.DataFrame(data)

        if os.path.exists(excel_file):
            existing = pd.read_excel(excel_file, engine='openpyxl')
            df = pd.concat([existing, df], ignore_index=True)

        df.to_excel(excel_file, index=False, engine='openpyxl')

        return redirect('/')
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contact")
    contacts = cursor.fetchall()
    conn.close()
    return render_template('admin.html', contacts=contacts)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/')

@app.route('/consultancy')
def consultancy():
    return render_template('consultancy.html')

@app.route('/training')
def training():
    return render_template('training.html')

@app.route('/report-making')
def report_making():
    return render_template('report.html')

@app.route('/resume-making')
def resume_making():
    return render_template('resume.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
