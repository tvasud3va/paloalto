from datetime import datetime
from pytz import timezone
from jinja2 import Environment, FileSystemLoader

# Import custom modules or external libraries
from infrastructure import weather, quotes

def main():
    """Compile variables and pass into README"""

    # Fetch weather information using the OpenWeather API for Palo Alto (or your specific location)
    (
        weather_dict,
        city_temperature,
        sunrise_time_unix,
        sunset_time_unix,
    ) = weather.get_openweather_info(city="Palo Alto")

    # Convert sunrise and sunset timestamps to Pacific Standard Time (PST)
    timestamp = weather.convert_timestamp_to_PST(sunrise_time_unix)
    formatted_time = timestamp.strftime("%H:%M %p")
    sunrise_time = str(formatted_time)

    # Convert sunset time from 24-hour to 12-hour clock
    sunset_time = weather.convert_timestamp_to_PST(sunset_time_unix).strftime("%H:%M")
    sunset_time = datetime.strptime(sunset_time, "%H:%M").strftime("%I:%M %p")

    # Get current time and date in PST
    current_time_PST = datetime.now(timezone("US/Pacific")).strftime("%H:%M")
    current_time_PST = datetime.strptime(current_time_PST, "%H:%M").strftime("%I:%M %p")
    current_date = datetime.now(timezone("US/Pacific")).strftime("%Y-%m-%d")

    # Fetch a random quote and its author
    rand_quote, rand_author = quotes.random_quote()

    # Get current air quality information
    aqi, pm10 = weather.get_openweather_air_quality()

    # Update PM10.json, render plot, and grab summary data
    weather.update_PM10_json(f"{current_date} {current_time_PST}", pm10, aqi)
    weather.render_PM10_plots()
    pm10_data_point_count, count_exceeding_EPA, days_of_AQI_data = \
        weather.summarize_PM10_json()
    days_exceeding_EPA_percentage = round((count_exceeding_EPA / pm10_data_point_count)*100, 1)

    # Define template variables with gathered information
    template_variables = {
        "state_name": "California",  # Adjust state name if needed
        "current_datetime_PST": f"{current_date} {current_time_PST}",
        "current_time_PST": datetime.now(timezone("US/Pacific")).strftime("%I:%M %p"),
        "sun_rise": sunrise_time,
        "sun_set": sunset_time,
        "temperature": city_temperature,
        "weather_emoji": weather.weather_icon(city_temperature),
        "rand_quote": rand_quote,
        "rand_author": rand_author,
        "AQI": aqi,
        "PM10": pm10,
        "days_of_AQI_data": days_of_AQI_data,
        "count_exceeding_EPA": count_exceeding_EPA,
        "pm10_data_point_count": pm10_data_point_count,
        "days_exceeding_EPA_percentage": str(days_exceeding_EPA_percentage) + "%",
        "PM10_plots_HTML": weather.generate_html_for_png_files()
    }

    # Load Jinja2 template, pass in variables, and render HTML
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("main.html")
    output_from_parsed_template = template.render(template_variables)

    # Write the rendered HTML to README.md
    with open("README.md", "w+") as fh:
        fh.write(output_from_parsed_template)

    # Generate markdown content
    markdown_content = f"""
    # Weather and Air Quality Report

    - Current Temperature: {city_temperature}°C
    - Sunrise Time: {sunrise_time}
    - Sunset Time: {sunset_time}
    - ...

    Generated at: {current_date} {current_time_PST}
    """

    # Write the markdown content to a file
    with open("output.md", "w") as md_file:
        md_file.write(markdown_content)

if __name__ == "__main__":
    # Execute the main function if the script is run as the main module
    main()
