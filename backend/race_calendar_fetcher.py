import os
import json
import datetime
import logging
import pandas as pd
import fastf1

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
    """Fetch F1 race calendar data."""
    
    def __init__(self, year=DEFAULT_YEAR, data_dir=None):
        """Initialize the RaceCalendarFetcher.
        
        Args:
            year (int): The F1 season year to fetch data for.
            data_dir (str): Directory path to store calendar data.
        """
        self.year = year
        
        if data_dir is None:
            # Use default directory under the package directory
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        else:
            self.data_dir = data_dir
            
        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File path for saved calendar data
        self.calendar_file = os.path.join(self.data_dir, f'f1_calendar_{self.year}.json')
        
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
            schedule = fastf1.get_event_schedule(self.year)
            
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
            schedule (DataFrame): The raw schedule data from FastF1.
            
        Returns:
            dict: Processed calendar data.
        """
        # Current date for determining past/future races
        now = datetime.datetime.now(datetime.timezone.utc)
        
        races = []
        
        # Process each race event
        for _, event in schedule.iterrows():
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
            
            # Create race dictionary
            race = {
                "round": int(event['RoundNumber']) if not pd.isna(event['RoundNumber']) else None,
                "country": event['Country'] if not pd.isna(event['Country']) else "",
                "location": event['Location'] if not pd.isna(event['Location']) else "",
                "name": event['EventName'] if not pd.isna(event['EventName']) else "",
                "official_name": event['OfficialEventName'] if 'OfficialEventName' in event and not pd.isna(event['OfficialEventName']) else "",
                "date": race_date_str,
                "status": status,
                "is_sprint": is_sprint,
                "format": event['EventFormat'] if not pd.isna(event['EventFormat']) else "",
                "sessions": session_dates
            }
            
            races.append(race)
        
        # Sort races by round number
        races.sort(key=lambda x: x["round"] if x["round"] is not None else 999)
        
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
            with open(self.calendar_file, 'w') as f:
                json.dump(calendar_data, f, indent=2)
            logger.info(f"Saved calendar data to {self.calendar_file}")
        except Exception as e:
            logger.error(f"Error saving calendar data: {e}")
    
    def get_next_race(self):
        """Get information about the next upcoming race.
        
        Returns:
            dict: Next race information or None if not found.
        """
        calendar_data = self.fetch_f1_calendar()
        
        # Find the first race in the future
        upcoming_races = [race for race in calendar_data.get("races", []) 
                         if race["status"] in ["future", "current"]]
        
        if not upcoming_races:
            logger.info("No upcoming races found")
            return None
        
        # Sort by date and get the first one
        upcoming_races.sort(key=lambda x: x["date"] if x["date"] else "9999-12-31")
        return upcoming_races[0]
    
    def update_calendar(self):
        """Force an update of the calendar data.
        
        Returns:
            dict: Updated calendar data.
        """
        return self.fetch_f1_calendar(force_refresh=True)


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