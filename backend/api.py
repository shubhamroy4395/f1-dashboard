from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from race_calendar_fetcher import RaceCalendarFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default year for calendar
DEFAULT_YEAR = 2025

# Initialize the app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize data directory
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Create race calendar fetcher
race_calendar = RaceCalendarFetcher(year=DEFAULT_YEAR, data_dir=data_dir)

@app.route('/')
def index():
    return jsonify({
        'message': 'F1 Dashboard API',
        'version': '1.0.0',
        'endpoints': [
            '/calendar',
            '/calendar/<int:year>',
            '/next-race'
        ]
    })

@app.route('/calendar')
def get_calendar():
    """Get the current season calendar"""
    calendar_data = race_calendar.fetch_f1_calendar()
    return jsonify(calendar_data)

@app.route('/calendar/<int:year>')
def get_calendar_for_year(year):
    """Get calendar for a specific year"""
    # Create a new fetcher for the requested year
    year_fetcher = RaceCalendarFetcher(year=year, data_dir=data_dir)
    calendar_data = year_fetcher.fetch_f1_calendar()
    return jsonify(calendar_data)

@app.route('/calendar/update')
def update_calendar():
    """Force an update of the calendar data"""
    calendar_data = race_calendar.update_calendar()
    return jsonify(calendar_data)

@app.route('/next-race')
def get_next_race():
    """Get information about the next race"""
    next_race = race_calendar.get_next_race()
    if next_race:
        return jsonify(next_race)
    else:
        return jsonify({'error': 'No upcoming races found'}), 404

@app.route('/race/<int:round>')
def get_race_by_round(round):
    """Get information about a specific race by round number"""
    calendar_data = race_calendar.fetch_f1_calendar()
    
    # Find the race with the specified round number
    race = next((r for r in calendar_data.get('races', []) if r.get('round') == round), None)
    
    if race:
        return jsonify(race)
    else:
        return jsonify({'error': f'Race with round {round} not found'}), 404

@app.route('/drivers')
def get_drivers():
    """Get a list of drivers for the current season"""
    # Placeholder for driver data - will implement in future
    return jsonify({'message': 'Driver data endpoint coming soon'})

if __name__ == '__main__':
    # Run the app in development mode
    app.run(debug=True, host='0.0.0.0', port=5000) 