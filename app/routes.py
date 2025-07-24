import os
from datetime import datetime
import sqlite3
import csv
import io

from flask import Blueprint, render_template, request, redirect, flash, url_for, session, Response
from utils import send_reset_email

main = Blueprint('main', __name__, template_folder='templates')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '../attendance.db')

EMAIL_USER = "lovequee5577@gmail.com"
EMAIL_PASS = "vspclihiulepnwiu"

SECRET_KEY = "admin_harvesters"


@main.route('/')
def home():
    return render_template('checkin.html')


@main.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    department = request.form['department']
    action = request.form['action']
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if action == 'Check In':
        cursor.execute('INSERT INTO checkin (name, department, date, time) VALUES (?, ?, ?, ?)',
                       (name, department, date_str, time_str))
    elif action == 'Check Out':
        cursor.execute('INSERT INTO checkout (name, department, date, time) VALUES (?, ?, ?, ?)', 
                       (name, department, date_str, time_str))

    cursor.execute('''
        SELECT time FROM checkin
        WHERE name = ? AND department = ? AND date = ?
        ORDER BY time DESC LIMIT 1
    ''', (name, department, date_str))
    checkin_record = cursor.fetchone()

    cursor.execute('''
        SELECT time FROM checkout
        WHERE name = ? AND department = ? AND date = ?
        ORDER BY time DESC LIMIT 1
    ''', (name, department, date_str))
    checkout_record = cursor.fetchone()

    check_in_time = checkin_record[0] if checkin_record else None
    check_out_time = checkout_record[0] if checkout_record else None


    cursor.execute('SELECT * FROM attendance_merged WHERE name = ? AND department = ? AND date = ?', 
                   (name, department, date_str))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('''
            UPDATE attendance_merged
            SET check_in = ?, check_out = ?
            WHERE name = ? AND department = ? AND date = ?
        ''', (check_in_time, check_out_time, name, department, date_str))
    else:
        cursor.execute('''
            INSERT INTO attendance_merged (name, department, date, check_in, check_out)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, department, date_str, check_in_time, check_out_time))

    conn.commit()
    conn.close()

    flash("Attendance submitted successfully.")
    return redirect('/')


@main.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password123':
            session['admin_logged_in'] = True
            session['admin_name'] = username
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('admin_login.html')


@main.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, department, date, check_in, check_out
        FROM attendance_merged
        ORDER BY id ASC
    """)
    records = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', records=records)


@main.route('/export_csv')
def export_csv():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, department, date, check_in, check_out FROM attendance_merged")
    data = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Department', 'Date', 'Check In', 'Check Out'])
    for row in data:
        writer.writerow(row)

    output.seek(0)
    conn.close()

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=attendance_data.csv"}
    )


@main.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin_login'))


@main.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        user_email = request.form.get("email")
        reset_link = f"http://127.0.0.1:5000/reset_password/{user_email}"
        send_reset_email(user_email, reset_link)
        flash("If this email exists, a password reset link has been sent.")
        return redirect(url_for('main.admin_login'))

    return render_template("forgot_password.html")

