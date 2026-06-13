from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = "awsproject123"

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if email == "admin@gmail.com" and password == "1234":
        session['user'] = email
        return render_template('dashboard.html')
    else:
        return render_template(
            'login.html',
            error="Invalid Email or Password ❌"
        )

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)