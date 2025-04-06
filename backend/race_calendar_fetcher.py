import os
import json
import datetime
import logging
import pandas as pd
import fastf1
from fastf1 import events

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default year for calendar
DEFAULT_YEAR = 2025

# Configure FastF1 cache
cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

class RaceCalendarFetcher:
    """Class to fetch and process F1 race calendar data"""
    
    def __init__(self, data_dir="data", cache_dir="cache"):
        """Initialize with the directory for storing data"""
        self.data_dir = data_dir
        self.year = DEFAULT_YEAR
        self.calendar_file = os.path.join(self.data_dir, f'f1_calendar_{self.year}.json')
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
            
        # Enable FastF1 cache
        try:
            fastf1.Cache.enable_cache(cache_dir)
            logger.info(f"FastF1 cache enabled: {cache_dir}")
        except Exception as e:
            logger.warning(f"Failed to enable FastF1 cache: {e}")

    def get_calendar(self, year=DEFAULT_YEAR):
        """Get the F1 calendar for the specific year.
        
        Args:
            year (str): The year to fetch the calendar for.
            
        Returns:
            dict: Calendar data including race schedule.
        """
        # Update the year if changed
        if str(year) != str(self.year):
            self.year = str(year)
            self.calendar_file = os.path.join(self.data_dir, f'f1_calendar_{self.year}.json')
        
        # Check if we have cached data
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'r') as f:
                    calendar_data = json.load(f)
                logger.info(f"Loaded cached calendar data for {self.year}")
                return calendar_data
            except Exception as e:
                logger.error(f"Error loading cached data: {str(e)}")
        
        # If no cached data or error loading it, fetch fresh data
        return self.fetch_f1_calendar(force_refresh=True)

    def fetch_f1_calendar(self, force_refresh=False):
        """Fetch the F1 calendar for the specified year.
        
        Args:
            force_refresh (bool): If True, fetches new data even if a cached version exists.
            
        Returns:
            dict: Calendar data including race schedule and other metadata.
        """
        # Check if we already have saved data and aren't forcing a refresh
        if os.path.exists(self.calendar_file) and not force_refresh:
            try:
                with open(self.calendar_file, 'r') as f:
                    calendar_data = json.load(f)
                logger.info(f"Loaded cached calendar data for {self.year}")
                return calendar_data
            except Exception as e:
                logger.warning(f"Error loading cached calendar data: {e}")
                # Fall through to fetch new data
        
        try:
            # Fetch the calendar using FastF1
            logger.info(f"Fetching F1 calendar for {self.year}")
            schedule = fastf1.get_event_schedule(int(self.year))
            
            # Process the calendar into our desired format
            calendar_data = self.process_calendar(schedule)
            
            # Save the processed data
            self.save_calendar_data(calendar_data)
            
            return calendar_data
            
        except Exception as e:
            logger.error(f"Error fetching F1 calendar: {e}")
            
            # If we have cached data, return that instead as fallback
            if os.path.exists(self.calendar_file):
                try:
                    with open(self.calendar_file, 'r') as f:
                        calendar_data = json.load(f)
                    logger.info(f"Using older cached calendar data as fallback")
                    return calendar_data
                except Exception as fallback_e:
                    logger.error(f"Error loading fallback calendar data: {fallback_e}")
            
            # No fallback available, return empty data
            return {"year": self.year, "races": [], "error": str(e)}
    
    def process_calendar(self, schedule):
        """Process the raw schedule into a structured calendar format.
        
        Args:
            schedule (DataFrame or dict): The raw schedule data from FastF1 or cached data.
            
        Returns:
            dict: Processed calendar data.
        """
        # If we already have processed data (dict with races key), return it directly
        if isinstance(schedule, dict) and 'races' in schedule:
            logger.info(f"Using pre-processed calendar data with {len(schedule['races'])} races")
            return schedule
            
        # Check if schedule is a DataFrame (from FastF1 API)
        if not isinstance(schedule, pd.DataFrame):
            logger.error(f"Invalid schedule format: expected DataFrame or processed dict, got {type(schedule)}")
            return {"year": self.year, "races": [], "error": "Invalid schedule format"}
        
        # Check if DataFrame is empty (using pandas DataFrame.empty attribute)
        try:
            if hasattr(schedule, 'empty') and schedule.empty:
                logger.warning(f"Empty schedule received for year {self.year}")
                return {"year": self.year, "races": [], "error": "Empty schedule"}
        except Exception as e:
            logger.warning(f"Error checking if schedule is empty: {e}")
            # Continue processing as best we can
        
        # Current date for determining past/future races
        now = datetime.datetime.now(datetime.timezone.utc)
        logger.info(f"Processing calendar for {self.year} at {now.isoformat()}")
        
        races = []
        
        # Process each race event
        for i, (_, event) in enumerate(schedule.iterrows()):
            # Log column names for the first event to help debugging
            if i == 0:
                logger.info(f"Schedule columns: {list(event.index)}")
                
            try:
                # Determine if this is a sprint weekend
                is_sprint = False
                event_format = str(event['EventFormat']).lower() if not pd.isna(event['EventFormat']) else ""
                if 'sprint' in event_format:
                    is_sprint = True
                    logger.info(f"Sprint weekend detected: {event['EventName']} - Format: {event_format}")
                
                # Extract race date
                race_date = None
                if 'Session5Date' in event and not pd.isna(event['Session5Date']):
                    # For sprint weekends, race is typically Session5
                    race_date = event['Session5Date']
                elif 'Session4Date' in event and not pd.isna(event['Session4Date']):
                    # For conventional weekends, might be Session4
                    race_date = event['Session4Date']
                elif 'EventDate' in event and not pd.isna(event['EventDate']):
                    # Fallback to EventDate
                    race_date = event['EventDate']
                
                # Convert race_date to standard format if it exists
                race_date_str = race_date.isoformat() if race_date is not None else None
                
                # Determine race status (past, current, future)
                status = "future"
                if race_date is not None:
                    # Ensure race_date is timezone-aware
                    if race_date.tzinfo is None:
                        # Convert naive datetime to UTC
                        race_date = race_date.replace(tzinfo=datetime.timezone.utc)
                    
                    if race_date < now:
                        status = "completed"
                    elif race_date.date() == now.date():
                        status = "current"
                
                # Create session dates dictionary
                session_dates = {}
                
                # Map session dates based on event format
                session_mappings = []
                if is_sprint:
                    # Sprint weekend session mapping
                    session_mappings = [
                        ("practice1", "Session1Date"),
                        ("sprint_qualifying", "Session2Date"),
                        ("sprint", "Session3Date"),
                        ("qualifying", "Session4Date"),
                        ("race", "Session5Date")
                    ]
                else:
                    # Conventional weekend session mapping
                    session_mappings = [
                        ("practice1", "Session1Date"),
                        ("practice2", "Session2Date"),
                        ("practice3", "Session3Date"),
                        ("qualifying", "Session4Date"),
                        ("race", "Session5Date")
                    ]
                
                # Extract session dates
                for session_key, date_field in session_mappings:
                    if date_field in event and not pd.isna(event[date_field]):
                        session_date = event[date_field]
                        # Ensure session_date is timezone-aware before isoformat
                        if session_date.tzinfo is None:
                            session_date = session_date.replace(tzinfo=datetime.timezone.utc)
                        session_dates[session_key] = session_date.isoformat()
                    else:
                        session_dates[session_key] = None
                
                # Get location details safely
                country = event['Country'] if 'Country' in event and not pd.isna(event['Country']) else ""
                location = event['Location'] if 'Location' in event and not pd.isna(event['Location']) else ""
                
                # Create race dictionary
                race = {
                    "round": int(event['RoundNumber']) if 'RoundNumber' in event and not pd.isna(event['RoundNumber']) else None,
                    "country": country,
                    "location": location,
                    "name": event['EventName'] if 'EventName' in event and not pd.isna(event['EventName']) else "",
                    "official_name": event['OfficialEventName'] if 'OfficialEventName' in event and not pd.isna(event['OfficialEventName']) else "",
                    "date": race_date_str,
                    "status": status,
                    "is_sprint": is_sprint,
                    "format": event['EventFormat'] if 'EventFormat' in event and not pd.isna(event['EventFormat']) else "",
                    "sessions": session_dates
                }
                
                races.append(race)
                logger.info(f"Processed race: {race['name']} - Round {race['round']}")
                
            except Exception as e:
                logger.error(f"Error processing race event: {str(e)}", exc_info=True)
                # Continue with next race rather than failing completely
        
        # Sort races by round number
        races.sort(key=lambda x: x["round"] if x["round"] is not None else 999)
        
        logger.info(f"Processed {len(races)} races for {self.year}")
        
        return {
            "year": self.year,
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "races": races
        }
    
    def save_calendar_data(self, calendar_data):
        """Save calendar data to JSON.
        
        Args:
            calendar_data (dict): The processed calendar data to save.
        """
        try:
            # Ensure data directory exists
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                
            with open(self.calendar_file, 'w') as f:
                json.dump(calendar_data, f, indent=2)
            logger.info(f"Calendar data saved to {self.calendar_file}")
        except Exception as e:
            logger.error(f"Error saving calendar data: {e}")
    
    def get_next_race(self, year=DEFAULT_YEAR):
        """Get the next race from the calendar"""
        try:
            calendar_data = self.get_calendar(year)
            
            if not calendar_data or 'races' not in calendar_data or not calendar_data['races']:
                logger.warning(f"No races found in calendar for {year}")
                return None
                
            # Current date for comparison
            now = datetime.datetime.now(datetime.timezone.utc)
            logger.info(f"Current date for next race check: {now.isoformat()}")
            
            # For testing/demo purposes: if all races are in the past, pretend first race is in the future
            all_in_past = True
            
            # Find upcoming races
            upcoming_races = []
            for race in calendar_data['races']:
                if 'date' not in race or not race['date']:
                    logger.warning(f"Race missing date: {race.get('name', 'Unknown')}")
                    continue
                    
                race_date = self._parse_date(race['date'])
                if not race_date:
                    logger.warning(f"Could not parse race date: {race['date']} for {race.get('name', 'Unknown')}")
                    continue
                
                # Ensure race_date is timezone-aware for comparison
                if race_date.tzinfo is None:
                    race_date = race_date.replace(tzinfo=datetime.timezone.utc)
                    logger.info(f"Converting naive datetime to timezone-aware for {race.get('name')}: {race_date.isoformat()}")
                
                try:
                    if race_date > now:
                        all_in_past = False
                        upcoming_races.append(race)
                        logger.info(f"Found upcoming race: {race['name']} on {race['date']}")
                except TypeError as e:
                    logger.error(f"Datetime comparison error for {race.get('name')}: {e}")
                    logger.error(f"Race date: {race_date} (tzinfo: {race_date.tzinfo}), Now: {now} (tzinfo: {now.tzinfo})")
                    # Try to fix it and compare again
                    try:
                        race_date = race_date.replace(tzinfo=datetime.timezone.utc)
                        if race_date > now:
                            all_in_past = False
                            upcoming_races.append(race)
                            logger.info(f"After fixing timezone: Found upcoming race: {race['name']} on {race['date']}")
                    except Exception as fix_error:
                        logger.error(f"Failed to fix timezone for comparison: {fix_error}")
            
            # If no upcoming races but we have races, return the first race for demo purposes
            if not upcoming_races and all_in_past and calendar_data['races']:
                # For demo/testing, pretend the first race is upcoming
                demo_race = calendar_data['races'][0].copy()  # Create a copy to avoid modifying original
                demo_race['status'] = 'future'  # Override status
                demo_race['demo_mode'] = True   # Add demo mode flag
                logger.info(f"No upcoming races found, using first race as demo: {demo_race['name']}")
                return demo_race
                
            if not upcoming_races:
                logger.warning(f"No upcoming races found for {year}")
                return None
                
            # Sort by date (earliest first)
            try:
                upcoming_races.sort(key=lambda x: self._parse_date(x['date']) or datetime.datetime.max.replace(tzinfo=datetime.timezone.utc))
            except Exception as sort_error:
                logger.error(f"Error sorting upcoming races: {sort_error}")
                # If sorting fails, just take the first one we found
                
            next_race = upcoming_races[0]
            logger.info(f"Next race: {next_race['name']} on {next_race['date']}")
            
            return next_race
            
        except Exception as e:
            logger.error(f"Error in get_next_race: {str(e)}", exc_info=True)
            raise

    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            logger.warning(f"Empty date string provided for parsing")
            return None
        try:
            return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None
    
    def get_race_by_round(self, round_number):
        """Get a race by its round number.
        
        Args:
            round_number (int): The round number of the race.
            
        Returns:
            dict: Race information or None if not found.
        """
        calendar_data = self.get_calendar()
        
        if not calendar_data or 'races' not in calendar_data:
            return None
            
        for race in calendar_data['races']:
            if race.get('round') == round_number:
                return race
                
        return None

    def _load_calendar_from_file(self):
        """Load calendar data from file"""
        try:
            # Check if cache file exists
            calendar_file = os.path.join(self.data_dir, f"f1_calendar_{self.year}.json")
            logger.info(f"Checking for cached calendar data in {calendar_file}")
            
            if os.path.exists(calendar_file):
                with open(calendar_file, 'r') as f:
                    calendar_data = json.load(f)
                logger.info(f"Loaded cached calendar data for {self.year}")
                return calendar_data
            else:
                logger.info(f"No cached calendar data found for {self.year}")
                return None
        except Exception as e:
            logger.error(f"Error loading calendar data from file: {str(e)}", exc_info=True)
            return None

# Example usage
if __name__ == "__main__":
    fetcher = RaceCalendarFetcher()
    print(f"Fetching F1 calendar for {DEFAULT_YEAR}...")
    calendar = fetcher.fetch_f1_calendar()
    
    # Print summary of races
    print(f"\nF1 {DEFAULT_YEAR} Calendar:")
    print(f"Total races: {len(calendar['races'])}")
    
    # Count sprint races
    sprint_races = [race for race in calendar['races'] if race['is_sprint']]
    print(f"Sprint races: {len(sprint_races)}")
    
    # Print next race
    print("\n--- Next Race Information ---")
    next_race = fetcher.get_next_race()
    if next_race:
        print(f"Round {next_race['round']}: {next_race['name']}")
        print(f"Location: {next_race['location']}, {next_race['country']}")
        print(f"Date: {next_race['date']}")
        print(f"Format: {next_race['format']}")
        print(f"Sprint weekend: {'Yes' if next_race['is_sprint'] else 'No'}")
        
        # Print session schedule
        print("\nSession Schedule:")
        for session_name, session_date in next_race['sessions'].items():
            if session_date:
                print(f"  {session_name.replace('_', ' ').title()}: {session_date}")
    else:
        print("No upcoming races found")
    
    # Check Chinese Grand Prix
    print("\n--- Chinese Grand Prix Information ---")
    china_races = [race for race in calendar['races'] if race['name'] and "Chinese" in race['name']]
    if china_races:
        china_race = china_races[0]
        print(f"Round {china_race['round']}: {china_race['name']}")
        print(f"Location: {china_race['location']}, {china_race['country']}")
        print(f"Format: {china_race['format']}")
        print(f"Sprint weekend: {'Yes' if china_race['is_sprint'] else 'No'}")
        
        # Print session schedule
        print("\nSession Schedule:")
        for session_name, session_date in china_race['sessions'].items():
            if session_date:
                print(f"  {session_name.replace('_', ' ').title()}: {session_date}")
    else:
        print("Chinese Grand Prix not found in calendar") 