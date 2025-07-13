from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'
API_KEY = "954272958625dd3272ba261c66b69770"

# Dummy database to simulate users
users = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        if mobile in users:
            return render_template('signup.html', error='User already exists.')
        users[mobile] = password
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        if mobile in users and users[mobile] == password:
            session['user'] = mobile
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def get_tips(temp, aqi):
    tips = []
    if temp >= 35:
        tips.append("Avoid outdoor activities during peak hours")
        tips.append("Stay hydrated and wear light clothing")
    if aqi >= 100:
        tips.append("Use a mask when stepping outside")
        tips.append("Keep indoor plants for better air quality")
    if not tips:
        tips.append("Weather and air quality are safe today! Enjoy your day!")
    return tips

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    weather_data = {}
    if request.method == 'POST':
        city = request.form['city']
        try:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(weather_url)
            data = response.json()
            if data.get('cod') != 200:
                weather_data['error'] = data.get('message', 'City not found.')
            else:
                temp = data['main']['temp']
                aqi = 90 + int(temp) % 40
                weather_data = {
                    'city': city.title(),
                    'temperature': temp,
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    'aqi': aqi,
                    'tips': get_tips(temp, aqi)
                }
        except Exception as e:
            weather_data['error'] = str(e)
    return render_template('index.html', data=weather_data)

@app.route('/api/trend/<city>')
def trend(city):
    mock_data = {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "temps": [30, 32, 31, 33, 34]
    }
    return jsonify(mock_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
