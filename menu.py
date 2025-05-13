from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests

API_KEY = "05bd8076417d8b663d519bd297478156"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
app = Flask(__name__)
app.secret_key = '123'
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


@app.route('/')
@app.route('/home')
def index():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['username'] = user.username
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
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken!', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/success')
def success():
    return render_template('dashboard.html', weather=None)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city')
    if not city:
        flash('Пожалуйста, введите название города', 'error')
        return redirect(url_for('success'))
    try:
        current_response = requests.get(
            BASE_URL,
            params={
                'q': city,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'ru'
            }
        )
        current_data = current_response.json()
        if current_response.status_code == 404 or current_data.get('cod') == '404':
            flash('Город не найден. Пожалуйста, проверьте название', 'error')
            return redirect(url_for('success'))
        if current_response.status_code != 200:
            flash('Ошибка при получении данных о погоде', 'error')
            return redirect(url_for('success'))
        forecast_response = requests.get(
            FORECAST_URL,
            params={
                'q': city,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'ru'
            }
        )
        forecast_data = forecast_response.json()
        forecast_list = forecast_data['list']
        dates = []
        temps = []
        for forecast in forecast_list:
            dates.append(forecast['dt_txt'])
            temps.append(forecast['main']['temp'])
        weather_data = {
            'city': current_data['name'],
            'temperature': current_data['main']['temp'],
            'description': current_data['weather'][0]['description'],
            'icon': current_data['weather'][0]['icon'],
            'humidity': current_data['main']['humidity'],
            'wind': current_data['wind']['speed'],
            'time': 'Now',
            'forecast_dates': dates,
            'forecast_temps': temps
        }
        return render_template('dashboard.html', weather=weather_data)
    except Exception as e:
        flash('Произошла ошибка при запросе данных о погоде', 'error')
        return redirect(url_for('success'))