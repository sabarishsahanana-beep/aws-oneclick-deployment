from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "awsproject123"

def get_total_users():

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")

    total = cursor.fetchone()[0]

    conn.close()

    return total


# HOME
@app.route('/')
def home():
    return render_template('login.html')


# LOGIN
@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        session['user'] = user[0]
        return render_template('dashboard.html')

    return render_template(
        'login.html',
        error="Invalid Email or Password ❌"
    )

# REGISTER PAGE
@app.route('/register')
def register_page():
    return render_template('register.html')


# REGISTER FORM
@app.route('/register', methods=['POST'])
def register():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()

        return render_template(
            'register.html',
            error="Email Already Registered ❌"
        )

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, password)
    )

    conn.commit()
    conn.close()

    return render_template(
        'register_success.html',
        name=name
    )


# USERS LIST
@app.route('/users')
def users_list():

    search = request.args.get('search')

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    if search:

        cursor.execute(
    """
    SELECT id, name, email, password
    FROM users
    WHERE name LIKE ? OR email LIKE ?
    """,
    (
        '%' + search + '%',
        '%' + search + '%'
    )
)
    else:

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            """
        )

    users = cursor.fetchall()

    # Search result count
    total_users = len(users)

    conn.close()

    return render_template(
        'users.html',
        users=users,
        total_users=total_users
    )


# DELETE USER
@app.route('/delete/<email>')
def delete_user(email):

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE email=?",
        (email,)
    )

    conn.commit()
    conn.close()

    return redirect('/users')


# EDIT USER
@app.route('/edit/<email>', methods=['GET', 'POST'])
def edit_user(email):

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        new_email = request.form['email']
        password = request.form['password']

        cursor.execute(
            """
            UPDATE users
            SET name=?, email=?, password=?
            WHERE email=?
            """,
            (name, new_email, password, email)
        )

        conn.commit()
        conn.close()

        return redirect('/users')

    cursor.execute(
        """
        SELECT name, email, password
        FROM users
        WHERE email=?
        """,
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_user.html',
        user=user
    )

# PROFILE PAGE
@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "profile.html",
        username=session["user"]
    )
# DASHBOARD
@app.route("/dashboard")
def dashboard():

    total_users = get_total_users()

    return render_template(
        "dashboard.html",
        total_users=total_users
    )

# EXPORT CSV
@app.route('/export')
def export_users():

    conn = sqlite3.connect('/data/users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email FROM users"
    )

    users = cursor.fetchall()

    conn.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID', 'Name', 'Email'])

    for user in users:
        writer.writerow(user)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=users.csv"
        }
    )


# LOGOUT
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('home'))


# RUN APP
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )