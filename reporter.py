import requests
import csv
import os
from pathlib import Path

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CSV_FILE = Path("city_weather_data.csv")

def city_name_input():
    """Prompt user for a city name until a valid city name is entered"""
    while True:
        city_name = input("Enter a city name: ").strip().title()
        if city_name:
            return city_name
        print("Please enter a valid city name.")


def fetch_weather_data(city_name):
    """Get weather data from the OpenWeatherMap API"""
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    parameters = {"q": city_name, "appid": API_KEY, "units": "metric"}

    try:
        # Make request to API
        api_response = requests.get(api_url, params=parameters, timeout=5)
        api_response.raise_for_status()

        # Convert response to JSON
        weather_data = api_response.json()

        # API gives a code != 200 if city not found
        if weather_data.get("cod") != 200:
            print(f"City '{city_name}' not found.")
            return None
        return weather_data
    except requests.RequestException as exception:
        print(f"Error fetching weather data: {exception}")
        return None


def extract_weather_info(weather_data):
    """Gather weather information into a dictionary"""
    return {
        "City": weather_data["name"],
        "Country": weather_data["sys"]["country"],
        "Temperature (C)": weather_data["main"]["temp"],
        "Humidity (%)": weather_data["main"]["humidity"],
        "Description": weather_data["weather"][0]["description"]
    }


def save_weather_info_to_csv(weather_info):
    """Save weather information to the CSV file"""
    # Check if file exists already
    headers_needed = not CSV_FILE.exists()

    # Open CSV file to append it
    with CSV_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=weather_info.keys())
        if headers_needed:
            # Write headers if needed
            csv_writer.writeheader()
        csv_writer.writerow(weather_info)


def summarize_weather_csv():
    """Print a summary of all cities saved in the CSV."""
    # No data if no file
    if not CSV_FILE.exists():
        print("No weather data available yet.")
        return

    # Read info from CSV
    with CSV_FILE.open("r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        city_weather_list = list(csv_reader)

    # Print number of cities and their temperature
    print(f"\nReport: {len(city_weather_list)} cities recorded in {CSV_FILE.name}:")
    for city_weather in city_weather_list:
        print(f"- {city_weather['City']} ({city_weather['Temperature (C)']} °C)")


def main():
    """Main loop for weather reporter"""
    city_name = city_name_input()
    weather_data = fetch_weather_data(city_name)
    
    # Extract and display weather info
    if weather_data:
        weather_info = extract_weather_info(weather_data)
        print(
            f"The weather in {weather_info['City']}, {weather_info['Country']} is "
            f"{weather_info['Description']} with {weather_info['Temperature (C)']} °C "
            f"and humidity of {weather_info['Humidity (%)']}%."
        )

        save_weather_info_to_csv(weather_info)
        summarize_weather_csv()
        
        print("\n Thank you for using the city weather reporter! See you again soon!")

if __name__ == "__main__":
    main()
