# F1 Dashboard Checkpoint - 2025-04-06

This file marks a checkpoint of the F1 Dashboard codebase that can be used for reverting to a known working state.

## Current Structure

```
E:\F1Dashboard\
├── README.md                  # Architecture overview
├── test_calendar.py           # Test script to display race calendar
├── CHECKPOINT.md              # This file - checkpoint documentation
└── backend\
    ├── api.py                 # Flask API endpoints
    ├── race_calendar_fetcher.py # Race calendar data fetcher
    ├── requirements.txt       # Python dependencies
    ├── cache\                 # FastF1 cache directory
    └── data\                  # Data storage directory
```

## Key Features Implemented

1. **Race Calendar Fetcher**
   - Retrieves F1 race calendars using FastF1 API
   - Processes and structures the data
   - Handles both regular and sprint race formats
   - Provides detailed session information
   - Includes cache support for faster access

2. **REST API**
   - `/api/calendar/<year>` - Get F1 race calendar for a specific year
   - `/api/next-race` - Get information about the next upcoming race
   - `/api/calendars` - Get calendars for multiple years with optional year range

3. **Test Calendar Script**
   - Displays full season calendar
   - Shows sprint race specific information
   - Provides details about the next race
   - Formatted output using Rich library

## Issues Fixed

1. **Sprint Race Detection**
   - Improved detection of sprint races by checking for 'sprint' substring in event format
   - Added `is_sprint_weekend` flag for easier checking
   - Created dedicated sprint race display

2. **Date Handling Error**
   - Fixed NaT error by adding proper null checks for session dates
   - Added exception handling for date parsing

3. **Default Year**
   - Set 2025 as the default year using a global constant

## Next Steps

1. Create a FastF1 field reference document
2. Implement driver and team data fetchers
3. Add results and standings endpoints
4. Develop telemetry visualization components
5. Build frontend application

## How to Run

1. Start the API server:
```
cd E:\F1Dashboard\backend
python api.py
```

2. Run the test script:
```
cd E:\F1Dashboard
python test_calendar.py
```

## Checkpoint 3: GitHub and Netlify Setup (2025-04-07)

### Summary
This checkpoint represents the preparation of the F1 Dashboard project for deployment to GitHub and Netlify. Key improvements include:

- Created `netlify.toml` configuration file for Netlify deployment
- Added serverless function handler (`api_handler.py`) to adapt the Flask API
- Updated frontend to support both local and deployed environments
- Added `.gitignore` file for proper version control
- Updated documentation with deployment instructions

### Changes
1. Created a Netlify configuration file with appropriate redirects
2. Implemented a serverless function handler to adapt the Flask API
3. Modified the frontend to dynamically detect environment (local vs. Netlify)
4. Added a `.gitignore` file to exclude unnecessary files from version control
5. Updated documentation with GitHub and Netlify deployment instructions

### Deployment Instructions
To deploy this project:

1. Push to GitHub:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/f1-dashboard.git
   git push -u origin main
   ```

2. Connect to Netlify:
   - Log in to Netlify
   - Create a new site from the GitHub repository
   - Configure the build settings as specified in the README
   - Deploy the site 