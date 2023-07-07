from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import openai
import os
load_dotenv()

app = Flask(__name__)
openai.api_key = os.environ.get('OPENAI_API_KEY')
open_weather_key = os.environ.get('OPENWEATHER_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            city = request.form['city']
            city = city.strip()
            weather = get_weather(city)
            city_info = get_city_info(city)
            return render_template('index.html', weather=weather, city_info=city_info)
        except Exception as e:
            error_message = f'Error retrieving data: {str(e)}'
            return render_template('index.html', error_message=error_message)
    return render_template('index.html')

def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={open_weather_key}'
    response = requests.get(url)
    data = response.json()

    if data['cod'] == 200:
        weather = {
            'city': data['name'],
            'temp': round(data['main']['temp']),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description']
        }
        return weather
    else:
        return None
    
def get_city_info(city):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                        {"role": "system", "content": "You are a helpful assistant that only generates responses with less than 2000 characters."},
                        {"role": "user", "content": f"What can you tell me about {city}?"}
            ])
        city_info = response['choices'][0]['message']['content']
        if "I'm sorry, but I couldn't find any information" in city_info:
            raise ValueError('City not found. Try again!')
        return city_info
    except openai.error.OpenAIError as e:
        error_message = e.response['error']['message']
        if 'City not found' in error_message:
            raise ValueError('City not found. Try again!!')
        else:
            print(f'Error: {error_message}')
            return None

if __name__ == '__main__':
    app.run(debug=True)