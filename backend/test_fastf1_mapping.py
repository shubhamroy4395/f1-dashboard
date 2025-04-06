import fastf1
import pandas as pd
import json
import os
import logging
from pprint import pprint
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S,%f'
)
logger = logging.getLogger(__name__)

# Set default year to 2025 for F1 Dashboard
DEFAULT_F1_YEAR = 2025

# Configure FastF1 cache
fastf1.Cache.enable_cache('cache')

# Custom JSON encoder to handle pandas NaT values
class FastF1Encoder(json.JSONEncoder):
    def default(self, obj):
        # Check if the object is a pandas NaT type
        if pd.isna(obj):
            return None
        # Let the base class handle everything else
        return super().default(obj)

def test_event_schedule_fields():
    """
    Test to verify that all expected fields are present in the event schedule data
    and document any new or changed fields.
    """
    logger.info("Testing event schedule fields...")
    
    # Fields we expect according to our documentation
    expected_fields = [
        'RoundNumber', 'Country', 'Location', 'EventName', 'EventDate', 'EventFormat',
        'Session1Date', 'Session2Date', 'Session3Date', 'Session4Date', 'Session5Date',
        'F1ApiSupport'
    ]
    
    # Get schedule for current year
    schedule = fastf1.get_event_schedule(DEFAULT_F1_YEAR)
    
    if schedule.empty:
        logger.error(f"No schedule found for {DEFAULT_F1_YEAR}")
        return False
    
    # Get actual fields from the data
    actual_fields = schedule.columns.tolist()
    
    # Check for missing fields
    missing_fields = [field for field in expected_fields if field not in actual_fields]
    if missing_fields:
        logger.warning(f"Missing expected fields: {missing_fields}")
    
    # Check for new fields
    new_fields = [field for field in actual_fields if field not in expected_fields]
    if new_fields:
        logger.info(f"New fields discovered: {new_fields}")
    
    # Log all fields for reference
    logger.info(f"All fields in schedule: {actual_fields}")
    
    return len(missing_fields) == 0

def test_event_formats():
    """
    Test to verify all event formats in the schedule and document any new formats.
    """
    logger.info("Testing event formats...")
    
    # Event formats we expect according to our documentation
    expected_formats = ['conventional', 'sprint', 'sprint_qualifying', 'sprint_shootout', 'testing']
    
    # Get schedules for last year, current year, and next year to capture more formats
    years_to_check = [DEFAULT_F1_YEAR - 1, DEFAULT_F1_YEAR, DEFAULT_F1_YEAR + 1]
    
    actual_formats = set()
    for year in years_to_check:
        try:
            schedule = fastf1.get_event_schedule(year)
            if not schedule.empty:
                # Add formats from this year to our set
                year_formats = schedule['EventFormat'].unique().tolist()
                actual_formats.update(year_formats)
        except Exception as e:
            logger.warning(f"Error fetching schedule for {year}: {str(e)}")
    
    # Check for new formats
    new_formats = [fmt for fmt in actual_formats if fmt not in expected_formats]
    if new_formats:
        logger.warning(f"New event formats discovered: {new_formats}")
    
    # Log all formats for reference
    logger.info(f"All event formats across years: {list(actual_formats)}")
    
    # Check our sprint detection logic on all formats
    for fmt in actual_formats:
        is_sprint = 'sprint' in str(fmt).lower()
        logger.info(f"Format '{fmt}' - Is Sprint: {is_sprint}")
    
    return True

def test_sprint_events():
    """
    Test to verify sprint events have the correct session structure 
    and document session naming patterns.
    """
    logger.info("Testing sprint events structure...")
    
    # Get schedule for current year
    schedule = fastf1.get_event_schedule(DEFAULT_F1_YEAR)
    
    if schedule.empty:
        logger.error(f"No schedule found for {DEFAULT_F1_YEAR}")
        return False
    
    # Filter for events that contain 'sprint' in their format
    sprint_events = schedule[schedule['EventFormat'].str.contains('sprint', case=False, na=False)]
    
    if sprint_events.empty:
        logger.warning(f"No sprint events found for {DEFAULT_F1_YEAR}")
        return True
    
    # Examine the first sprint event in detail
    sprint_event = sprint_events.iloc[0]
    
    # Log the event details
    logger.info(f"Examining sprint event: {sprint_event['EventName']}")
    logger.info(f"Event format: {sprint_event['EventFormat']}")
    
    # Check session dates
    session_fields = ['Session1Date', 'Session2Date', 'Session3Date', 'Session4Date', 'Session5Date']
    for field in session_fields:
        if field in sprint_event and pd.notna(sprint_event[field]):
            logger.info(f"{field}: {sprint_event[field]}")
        else:
            logger.warning(f"{field} is missing or NaN for this sprint event")
    
    # Print the number of sprint events
    logger.info(f"Total sprint events for {DEFAULT_F1_YEAR}: {len(sprint_events)}")
    
    # Log all sprint event names
    sprint_names = sprint_events['EventName'].tolist()
    logger.info(f"Sprint events: {sprint_names}")
    
    return True

def test_session_results():
    """
    Test loading session results for a completed race to verify field structure.
    """
    logger.info("Testing session results fields...")
    
    # Expected fields in session results
    expected_result_fields = [
        'DriverNumber', 'Driver', 'TeamName', 'Position', 'Points', 
        'Time', 'Status', 'FastestLap', 'GridPosition', 'FirstName', 
        'LastName', 'Nationality'
    ]
    
    # Get schedule for current year
    schedule = fastf1.get_event_schedule(DEFAULT_F1_YEAR)
    
    if schedule.empty:
        logger.error(f"No schedule found for {DEFAULT_F1_YEAR}")
        return False
    
    # Filter for completed events (those with date before current date)
    current_date = datetime.now()
    completed_events = schedule[pd.to_datetime(schedule['EventDate']) < current_date]
    
    if completed_events.empty:
        logger.warning(f"No completed events found for {DEFAULT_F1_YEAR}")
        # Try previous year
        prev_year = DEFAULT_F1_YEAR - 1
        prev_schedule = fastf1.get_event_schedule(prev_year)
        if prev_schedule.empty:
            logger.error(f"No schedule found for {prev_year} either")
            return False
        completed_events = prev_schedule
    
    # Get the most recent completed event
    event = completed_events.iloc[-1]
    
    try:
        # Load the race session
        session = fastf1.get_session(event['EventDate'].year, event['RoundNumber'], 'R')
        session.load()
        
        if session.results is None:
            logger.warning(f"No results available for {event['EventName']}")
            return False
        
        # Check result fields
        actual_fields = session.results.columns.tolist()
        
        # Check for missing fields
        missing_fields = [field for field in expected_result_fields if field not in actual_fields]
        if missing_fields:
            logger.warning(f"Missing expected result fields: {missing_fields}")
        
        # Check for new fields
        new_fields = [field for field in actual_fields if field not in expected_result_fields]
        if new_fields:
            logger.info(f"New result fields discovered: {new_fields}")
        
        # Log all fields for reference
        logger.info(f"All fields in results: {actual_fields}")
        
        return len(missing_fields) == 0
        
    except Exception as e:
        logger.error(f"Error loading session: {str(e)}")
        return False

def export_test_results(output_file='tests/fastf1_mapping_results.json'):
    """
    Export test results and discovered field mappings to a JSON file.
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'fields': {},
        'formats': {},
        'sprint_events': {},
        'result_fields': {}
    }
    
    # Get field mapping
    schedule = fastf1.get_event_schedule(DEFAULT_F1_YEAR)
    if not schedule.empty:
        results['fields']['all'] = schedule.columns.tolist()
        
        # Get sample event data
        sample_event = schedule.iloc[0].to_dict()
        # Convert datetime objects to strings
        for key, value in sample_event.items():
            if isinstance(value, pd.Timestamp):
                sample_event[key] = value.isoformat()
        results['fields']['sample'] = sample_event
    
    # Get event formats
    formats = []
    for year in [DEFAULT_F1_YEAR - 1, DEFAULT_F1_YEAR, DEFAULT_F1_YEAR + 1]:
        try:
            year_schedule = fastf1.get_event_schedule(year)
            if not year_schedule.empty:
                year_formats = year_schedule['EventFormat'].unique().tolist()
                formats.extend(year_formats)
        except:
            pass
    results['formats']['all'] = list(set(formats))
    
    # Get sprint events
    if not schedule.empty:
        sprint_events = schedule[schedule['EventFormat'].str.contains('sprint', case=False, na=False)]
        if not sprint_events.empty:
            results['sprint_events']['count'] = len(sprint_events)
            results['sprint_events']['names'] = sprint_events['EventName'].tolist()
            
            # Get sample sprint event
            sample_sprint = sprint_events.iloc[0].to_dict()
            # Convert datetime objects to strings
            for key, value in sample_sprint.items():
                if isinstance(value, pd.Timestamp):
                    sample_sprint[key] = value.isoformat()
            results['sprint_events']['sample'] = sample_sprint
    
    # Get result fields from a completed race if possible
    try:
        # Find a completed race
        completed_events = schedule[pd.to_datetime(schedule['EventDate']) < datetime.now()]
        if not completed_events.empty:
            event = completed_events.iloc[-1]
            session = fastf1.get_session(event['EventDate'].year, event['RoundNumber'], 'R')
            session.load()
            
            if session.results is not None:
                results['result_fields']['all'] = session.results.columns.tolist()
                
                # Get sample result
                if not session.results.empty:
                    sample_result = session.results.iloc[0].to_dict()
                    # Convert non-serializable objects to strings
                    for key, value in sample_result.items():
                        if not isinstance(value, (str, int, float, bool, type(None))):
                            sample_result[key] = str(value)
                    results['result_fields']['sample'] = sample_result
    except Exception as e:
        results['result_fields']['error'] = str(e)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, cls=FastF1Encoder)
    
    logger.info(f"Test results exported to {output_file}")
    return results

if __name__ == "__main__":
    print("\n=== FastF1 Mapping Regression Tests ===\n")
    
    # Run all tests
    field_test_result = test_event_schedule_fields()
    format_test_result = test_event_formats()
    sprint_test_result = test_sprint_events()
    results_test_result = test_session_results()
    
    # Export results to JSON
    export_results = export_test_results()
    
    # Output summary
    print("\n=== Test Results ===")
    print(f"Event Schedule Fields: {'PASS' if field_test_result else 'FAIL'}")
    print(f"Event Formats: {'PASS' if format_test_result else 'FAIL'}")
    print(f"Sprint Events: {'PASS' if sprint_test_result else 'FAIL'}")
    print(f"Session Results: {'PASS' if results_test_result else 'FAIL'}")
    
    if all([field_test_result, format_test_result, sprint_test_result, results_test_result]):
        print("\n✅ All tests passed! Our FastF1 mappings are accurate.")
    else:
        print("\n❌ Some tests failed. Review the logs for details and update the documentation.")
    
    print("\nDetailed results saved to 'tests/fastf1_mapping_results.json'") 