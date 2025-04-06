import json
import os
from urllib.parse import parse_qs
import fastf1
from race_calendar_fetcher import RaceCalendarFetcher

# Initialize FastF1 cache
try:
    if not os.path.exists('cache'):
        os.makedirs('cache')
    fastf1.Cache.enable_cache('cache')
except Exception as e:
    print(f"Warning: Cache setup failed - {str(e)}")

# Initialize fetcher
calendar_fetcher = RaceCalendarFetcher()

def handler(event, context):
    """Netlify function handler for API requests"""
    
    # Get the path parameter from query string
    path = event.get('queryStringParameters', {}).get('path', '') 
    if not path and event.get('path'):
        # Try to get from path directly
        path = event.get('path', '').lstrip('/')
    
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
        params = parse_qs(event.get('queryStringParameters', {}))
        year = params.get('year', ['2025'])[0]
        calendar_data = calendar_fetcher.get_calendar(year)
        return {
            'statusCode': 200,
            'body': json.dumps(calendar_data),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }
    
    elif path == 'next-race':
        next_race = calendar_fetcher.get_next_race()
        return {
            'statusCode': 200,
            'body': json.dumps(next_race),
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
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                }
            }
    
    # Default 404 response
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
    }