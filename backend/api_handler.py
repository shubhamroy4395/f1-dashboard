import json
import os
import fastf1
from race_calendar_fetcher import RaceCalendarFetcher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastF1 cache
cache_dir = os.environ.get('CACHE_DIR', './cache')
try:
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        logger.info(f"Created cache directory: {cache_dir}")
    
    fastf1.Cache.enable_cache(cache_dir)
    logger.info(f"FastF1 cache enabled at: {cache_dir}")
except Exception as e:
    logger.error(f"Cache setup failed: {str(e)}")

# Initialize fetcher
calendar_fetcher = RaceCalendarFetcher()

def handler(event, context):
    """Netlify function handler for API requests"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Get the path parameter from query string
    path = None
    
    # Try to get path from different event structures
    if event.get('queryStringParameters') and event['queryStringParameters'].get('path'):
        path = event['queryStringParameters']['path']
    elif event.get('path'):
        path = event.get('path', '').lstrip('/')
    elif event.get('rawUrl'):
        # Try to extract from raw URL if available
        url_parts = event['rawUrl'].split('/')
        if len(url_parts) > 3:
            path = url_parts[-1]
    
    logger.info(f"Resolved path: {path}")
    
    if not path:
        logger.error("No path parameter found in the request")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing path parameter'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }
    
    # Get HTTP method
    method = event.get('httpMethod', 'GET')
    
    if method != 'GET':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }
    
    # Route the request
    if path == 'calendar':
        # Get the year parameter if provided
        year = '2025'  # Default year
        if event.get('queryStringParameters') and event['queryStringParameters'].get('year'):
            year = event['queryStringParameters']['year']
        
        logger.info(f"Fetching calendar for year: {year}")
        try:
            calendar_data = calendar_fetcher.get_calendar(year)
            return {
                'statusCode': 200,
                'body': json.dumps(calendar_data),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
        except Exception as e:
            logger.error(f"Error fetching calendar: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Failed to fetch calendar: {str(e)}'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
    
    elif path == 'next-race':
        logger.info("Fetching next race")
        try:
            next_race = calendar_fetcher.get_next_race()
            return {
                'statusCode': 200,
                'body': json.dumps(next_race),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
        except Exception as e:
            logger.error(f"Error fetching next race: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Failed to fetch next race: {str(e)}'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
    
    elif path.startswith('race/'):
        try:
            # Extract round number from path
            parts = path.split('/')
            if len(parts) < 2:
                raise ValueError("Invalid race path")
            
            round_number = int(parts[1])
            logger.info(f"Fetching race by round: {round_number}")
            
            race_data = calendar_fetcher.get_race_by_round(round_number)
            
            if not race_data:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Race not found'}),
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    }
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps(race_data),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
        except (ValueError, IndexError) as e:
            logger.error(f"Error processing race request: {str(e)}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
    
    # Default 404 response
    logger.error(f"Path not found: {path}")
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
    }