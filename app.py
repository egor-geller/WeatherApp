from flask import Flask, render_template, request
import datetime
import requests
import json

app = Flask(__name__)

exclude = 'minutely,hourly'
lang = 'en'  # for hebrew change to he
unit = 'metric'  # for imperial change to imperial

with open("info.json", 'r') as file:
    config = json.load(file)
    API_KEY = config['key']


def get_city_coordinates(city_name, api_key):
    geocoding_url = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}'
    response = requests.get(geocoding_url)

    if response.status_code == 200 and len(response.json()) > 0:
        city_data = response.json()[0]
        return city_data['lat'], city_data['lon']
    else:
        return None, None


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city')
    date_str = request.form.get('date')

    # Convert the date from the form to a UNIX timestamp
    target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    unix_timestamp = int(target_date.timestamp())

    # For current and future weather, use the One Call API:
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{unix_timestamp}?key={API_KEY}&unitGroup={unit}'
    print(unix_timestamp)
    # Make the API request
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()  # Parse the JSON response

        if data['days']:
            current_temp = data['days'][0]['temp']

            return render_template('weather.html',
                                   city=city,
                                   date=date_str,
                                   current_temp=current_temp)
        else:
            return "Weather data not found for the selected date."
    else:
        return f"Error: {response.status_code}"


if __name__ == '__main__':
    app.run(debug=True)
