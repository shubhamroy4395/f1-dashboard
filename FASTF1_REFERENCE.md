# FastF1 API Reference

This document provides a reference for the FastF1 API fields, event formats, and data structures relevant to the F1 Dashboard project.

## Event Schedule Fields

These fields are available in the event schedule data returned by `fastf1.get_event_schedule()`:

| Field            | Type     | Description                                   | Example Value                                     |
|------------------|----------|-----------------------------------------------|-------------------------------------------------|
| RoundNumber      | integer  | Race weekend number in the season             | 2                                               |
| Country          | string   | Host country                                  | "China"                                         |
| Location         | string   | City/circuit location                         | "Shanghai"                                      |
| OfficialEventName| string   | Full official event name                      | "FORMULA 1 HEINEKEN CHINESE GRAND PRIX 2025"    |
| EventDate        | datetime | Main race date                                | "2025-03-23T00:00:00"                           |
| EventName        | string   | Short event name                              | "Chinese Grand Prix"                            |
| EventFormat      | string   | Format of the event (see Event Formats)       | "sprint_qualifying"                             |
| Session1         | string   | Name of the first session                     | "Practice 1"                                    |
| Session1Date     | datetime | Local date/time of the first session          | "2025-03-21T11:30:00+08:00"                     |
| Session1DateUtc  | datetime | UTC date/time of the first session            | "2025-03-21T03:30:00"                           |
| Session2         | string   | Name of the second session                    | "Sprint Qualifying"                             |
| Session2Date     | datetime | Local date/time of the second session         | "2025-03-21T15:30:00+08:00"                     |
| Session2DateUtc  | datetime | UTC date/time of the second session           | "2025-03-21T07:30:00"                           |
| Session3         | string   | Name of the third session                     | "Sprint"                                        |
| Session3Date     | datetime | Local date/time of the third session          | "2025-03-22T11:00:00+08:00"                     |
| Session3DateUtc  | datetime | UTC date/time of the third session            | "2025-03-22T03:00:00"                           |
| Session4         | string   | Name of the fourth session                    | "Qualifying"                                    |
| Session4Date     | datetime | Local date/time of the fourth session         | "2025-03-22T15:00:00+08:00"                     |
| Session4DateUtc  | datetime | UTC date/time of the fourth session           | "2025-03-22T07:00:00"                           |
| Session5         | string   | Name of the fifth session                     | "Race"                                          |
| Session5Date     | datetime | Local date/time of the fifth session          | "2025-03-23T15:00:00+08:00"                     |
| Session5DateUtc  | datetime | UTC date/time of the fifth session            | "2025-03-23T07:00:00"                           |
| F1ApiSupport     | boolean  | Whether the event is supported by the F1 API  | true                                            |

## Event Formats

The FastF1 API defines multiple event formats which determine the structure of the race weekend:

| Format             | Description                                       | Contains Sprint | Sessions                                                    |
|--------------------|---------------------------------------------------|----------------|-------------------------------------------------------------|
| conventional       | Standard race weekend with practice and qualifying | No             | Practice 1, Practice 2, Practice 3, Qualifying, Race         |
| sprint_qualifying  | Sprint weekend format                             | Yes            | Practice 1, Sprint Qualifying, Sprint, Qualifying, Race      |
| testing            | Pre-season testing events                         | No             | Practice 1, Practice 2, Practice 3                           |

### Sprint Events in 2025

The 2025 F1 calendar includes 6 sprint events:

1. Chinese Grand Prix
2. Miami Grand Prix
3. Belgian Grand Prix
4. United States Grand Prix
5. São Paulo Grand Prix
6. Qatar Grand Prix

## Session Results Fields

These fields are available in the session results data returned by `session.results`:

| Field               | Type     | Description                                | Example Value                                      |
|---------------------|----------|--------------------------------------------|---------------------------------------------------|
| DriverNumber        | string   | Driver's car number                        | "1"                                               |
| BroadcastName       | string   | Name as shown in broadcasts                | "M VERSTAPPEN"                                    |
| Abbreviation        | string   | Three-letter driver code                   | "VER"                                             |
| DriverId            | string   | Unique driver identifier                   | "max_verstappen"                                  |
| TeamName            | string   | Full team name                             | "Red Bull Racing"                                 |
| TeamColor           | string   | Team color in hex (without #)              | "3671C6"                                          |
| TeamId              | string   | Unique team identifier                     | "red_bull"                                        |
| FirstName           | string   | Driver's first name                        | "Max"                                             |
| LastName            | string   | Driver's last name                         | "Verstappen"                                      |
| FullName            | string   | Driver's full name                         | "Max Verstappen"                                  |
| HeadshotUrl         | string   | URL to driver's headshot image             | "https://media.formula1.com/..."                  |
| CountryCode         | string   | Driver's country code (may be empty)       | ""                                                |
| Position            | float    | Finishing position                         | 1.0                                               |
| ClassifiedPosition  | string   | Classified position string                 | "1"                                               |
| GridPosition        | float    | Starting grid position                     | 1.0                                               |
| Q1                  | datetime | Q1 time (can be NaT if not applicable)     | null                                              |
| Q2                  | datetime | Q2 time (can be NaT if not applicable)     | null                                              |
| Q3                  | datetime | Q3 time (can be NaT if not applicable)     | null                                              |
| Time                | timedelta| Race time                                  | "0 days 01:22:06.983000"                          |
| Status              | string   | Race finish status                         | "Finished"                                        |
| Points              | float    | Points earned in the session               | 25.0                                              |

## Implementation Notes

### Handling NaT Values

The FastF1 API may return pandas NaT (Not a Time) values for date/time fields that are not available or applicable. These values need special handling when serializing to JSON:

```python
import json
import pandas as pd

class FastF1Encoder(json.JSONEncoder):
    def default(self, obj):
        # Check if the object is a pandas NaT type
        if pd.isna(obj):
            return None
        # Let the base class handle everything else
        return super().default(obj)
        
# Use the custom encoder when dumping to JSON
json.dump(data, file, cls=FastF1Encoder)
```

### Sprint Format Detection

To properly detect and handle sprint events:

```python
def is_sprint_event(event):
    """Check if an event is a sprint event based on EventFormat."""
    if pd.isna(event['EventFormat']):
        return False
    
    return 'sprint' in event['EventFormat'].lower()
```

## Future Improvements

1. **Session Information**: Add more specific mapping for session information to better interpret different session names.

2. **Event Format Variations**: Monitor for new event formats that may be introduced in future seasons.

3. **Fallback Handling**: Implement more robust fallback handling for when API calls fail, especially for future race data.

4. **Caching Strategy**: Develop a more aggressive caching strategy to reduce dependency on API availability.

## Resources

- [FastF1 Documentation](https://docs.fastf1.dev/)
- [FastF1 GitHub Repository](https://github.com/theOehrly/Fast-F1) 