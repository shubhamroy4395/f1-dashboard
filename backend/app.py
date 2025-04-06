import os
import json
import logging
import traceback
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, send_from_directory, Response, request
from flask_cors import CORS
from race_calendar_fetcher import RaceCalendarFetcher, DEFAULT_YEAR

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize app
app = Flask(__name__, 
            static_folder='../static',
            template_folder='../')

# Configure CORS properly
CORS(app, resources={r"/*": {"origins": "*"}})

# Create cache and data directories if they don't exist
cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
data_dir = os.path.join(os.path.dirname(__file__), 'data')

for directory in [cache_dir, data_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

# Initialize race calendar fetcher
calendar_fetcher = RaceCalendarFetcher(data_dir=data_dir, cache_dir=cache_dir)

# Request logging middleware
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    if request.args:
        logger.info(f"Request args: {request.args}")

# API Routes
@app.route('/calendar')
@app.route('/calendar/<int:year>')
def get_calendar(year=DEFAULT_YEAR):
    try:
        logger.info(f"Fetching calendar for year: {year}")
        calendar_data = calendar_fetcher.get_calendar(str(year))
        
        if not calendar_data:
            logger.error(f"No calendar data returned for {year}")
            return jsonify({"error": "No calendar data available"}), 500
            
        if 'error' in calendar_data:
            logger.error(f"Error in calendar data: {calendar_data['error']}")
            return jsonify({"error": calendar_data['error']}), 500
            
        logger.info(f"Successfully fetched calendar with {len(calendar_data.get('races', []))} races")
        return jsonify(calendar_data)
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error fetching calendar: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details.split('\n')}), 500

@app.route('/next-race')
def get_next_race():
    try:
        logger.info("Fetching next race")
        next_race = calendar_fetcher.get_next_race()
        if next_race:
            logger.info(f"Next race found: {next_race.get('name')} (Round {next_race.get('round')})")
            # If there's a demo flag, indicate this in the response
            if next_race.get('status') == 'future' and next_race.get('demo_mode', False):
                logger.info("Returning demo race (no actual upcoming races found)")
                next_race['demo_mode'] = True
                next_race['demo_notice'] = "This is a demonstration race as there are no upcoming races in the calendar"
            return jsonify(next_race)
        else:
            logger.warning("No upcoming race found")
            # Create a demo race for testing when no races are found
            demo_race = {
                "name": "Demo Grand Prix",
                "round": 1,
                "country": "Demo Country",
                "location": "Demo Circuit",
                "date": (datetime.now() + timedelta(days=10)).isoformat(),
                "status": "future",
                "is_sprint": False,
                "format": "conventional",
                "demo_mode": True,
                "demo_notice": "This is a demonstration race as no races were found",
                "sessions": {
                    "practice1": (datetime.now() + timedelta(days=8)).isoformat(),
                    "practice2": (datetime.now() + timedelta(days=8, hours=4)).isoformat(),
                    "practice3": (datetime.now() + timedelta(days=9)).isoformat(),
                    "qualifying": (datetime.now() + timedelta(days=9, hours=4)).isoformat(),
                    "race": (datetime.now() + timedelta(days=10)).isoformat()
                }
            }
            logger.info("Returning demo race as fallback")
            return jsonify(demo_race)
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error fetching next race: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details.split('\n')}), 500

@app.route('/race/<int:round>')
def get_race_by_round(round):
    try:
        logger.info(f"Fetching race by round: {round}")
        race_data = calendar_fetcher.get_race_by_round(round)
        if race_data:
            logger.info(f"Race found: {race_data.get('name')}")
            return jsonify(race_data)
        else:
            logger.warning(f"Race with round {round} not found")
            return jsonify({"error": "Race not found", "message": f"No race found with round number {round}"}), 404
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error fetching race: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details.split('\n')}), 500

# Frontend Routes
@app.route('/')
def index():
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    logger.info(f"Serving static file: {path}")
    return send_from_directory('../static', path)

# Health check endpoint
@app.route('/health')
def health_check():
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "development"),
        "cache_dir": cache_dir,
        "data_dir": data_dir
    }
    logger.info(f"Health check: {status['status']}")
    return jsonify(status)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 error: {request.path}")
    return jsonify({"error": "Not found", "message": f"The requested URL {request.path} was not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error", "message": str(error)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting F1 Dashboard on port {port}")
    logger.info(f"Cache directory: {cache_dir}")
    logger.info(f"Data directory: {data_dir}")
    app.run(host='0.0.0.0', port=port, debug=True) 