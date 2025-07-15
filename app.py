from flask import Flask, render_template, request, redirect, session, url_for, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_key')

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

DB_PATH = '/tmp/database.db'
EXCEL_PATH = '/tmp/contacts.xlsx'

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
        print(f"[CONTACT FORM] Received: {name}, {email}, {mobile}, {message}")

        # Save to SQLite
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO contact (name, email, mobile, message) VALUES (?, ?, ?, ?)",
                     (name, email, mobile, message))
        conn.commit()
        conn.close()

        # Save to Excel
        data = {
            "Name": [name],
            "Email": [email],
            "Mobile": [mobile],
            "Message": [message]
        }
        df = pd.DataFrame(data)

        if os.path.exists(EXCEL_PATH):
            existing = pd.read_excel(EXCEL_PATH, engine='openpyxl')
            df = pd.concat([existing, df], ignore_index=True)

        df.to_excel(EXCEL_PATH, index=False, engine='openpyxl')

        return redirect('/')
    return render_template('contact.html')

@app.route('/download-contacts')
def download_contacts():
    if os.path.exists(EXCEL_PATH):
        return send_file(EXCEL_PATH, as_attachment=True)
    else:
        return "No contact data found.", 404

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
    conn = sqlite3.connect(DB_PATH)
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
