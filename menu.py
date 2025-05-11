from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '123'
users_db = {
    "q@q.q": {
        "username": "q",
        "password": "1"
    }
}


@app.route('/')
@app.route('/home')
def index():
    return render_template('sign_in.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if email in users_db and users_db[email]['password'] == password:
        return redirect(url_for('success'))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        if email in users_db:
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        users_db[email] = {
            "username": username,
            "password": password
        }

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('index'))

    return render_template('log_in.html')


@app.route('/success')
def success():
    return "Login successful!"
