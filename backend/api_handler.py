import os
import json
import logging
import traceback
from datetime import datetime, timedelta
import pathlib

from race_calendar_fetcher import RaceCalendarFetcher, DEFAULT_YEAR

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create cache and data directories
base_path = pathlib.Path(__file__).parent.resolve()
cache_dir = os.path.join(base_path, 'cache')
data_dir = os.path.join(base_path, 'data')

for directory in [cache_dir, data_dir]:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Created directory: {directory}")

# Initialize race calendar fetcher
calendar_fetcher = RaceCalendarFetcher(data_dir=data_dir, cache_dir=cache_dir)

def handler(event, context):
    """Main handler function for Netlify Functions"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Add CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 204,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Get the path from query parameters - this is set by netlify.toml redirects
        query_params = event.get('queryStringParameters', {}) or {}
        path = query_params.get('path', '')
        
        logger.info(f"Handling path: {path}")
        
        # Route to appropriate handler based on the path
        if path.startswith('calendar'):
            # Extract year if provided (calendar/2025)
            parts = path.split('/')
            year = DEFAULT_YEAR
            if len(parts) > 1 and parts[1].isdigit():
                year = parts[1]
                
            logger.info(f"Fetching calendar for year: {year}")
            try:
                calendar_data = calendar_fetcher.get_calendar(str(year))
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(calendar_data)
                }
            except Exception as e:
                logger.error(f"Error fetching calendar: {str(e)}", exc_info=True)
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({"error": str(e)})
                }
                
        elif path == 'next-race':
            logger.info("Fetching next race")
            try:
                next_race = calendar_fetcher.get_next_race()
                if next_race:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps(next_race)
                    }
                else:
                    # Create a demo race for testing
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
                        "sessions": {
                            "practice_1": (datetime.now() + timedelta(days=8)).isoformat(),
                            "practice_2": (datetime.now() + timedelta(days=8, hours=4)).isoformat(),
                            "practice_3": (datetime.now() + timedelta(days=9)).isoformat(),
                            "qualifying": (datetime.now() + timedelta(days=9, hours=4)).isoformat(),
                            "race": (datetime.now() + timedelta(days=10)).isoformat()
                        }
                    }
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps(demo_race)
                    }
            except Exception as e:
                logger.error(f"Error fetching next race: {str(e)}", exc_info=True)
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({"error": str(e)})
                }
                
        elif path.startswith('race/'):
            # Extract round number
            parts = path.split('/')
            if len(parts) < 2:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({"error": "Missing round number"})
                }
                
            try:
                round_number = int(parts[1])
                logger.info(f"Fetching race by round: {round_number}")
                race_data = calendar_fetcher.get_race_by_round(round_number)
                
                if race_data:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps(race_data)
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({"error": "Race not found"})
                    }
            except Exception as e:
                logger.error(f"Error fetching race: {str(e)}", exc_info=True)
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({"error": str(e)})
                }
        
        # Health check endpoint
        elif path == 'health':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat()
                })
            }
        
        # Default 404 response
        else:
            logger.error(f"Path not found: {path}")
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({"error": "Not found"})
            }
            
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }