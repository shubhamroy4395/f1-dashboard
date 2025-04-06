# F1 Dashboard

A modern dashboard for tracking Formula 1 race information using the FastF1 API.

## Features

- 📅 Complete 2025 F1 race calendar
- 🏎️ Next race information with countdown
- 🏁 Race weekend session schedules
- 🔄 Sprint weekend detection
- 💻 Modern, responsive UI inspired by F1's design language

## Project Structure

```
F1Dashboard/
├── backend/            # Flask API backend
│   ├── api.py          # API endpoints
│   ├── race_calendar_fetcher.py # Calendar data logic
│   ├── cache/          # FastF1 cache directory
│   └── tests/          # Test scripts
├── index.html          # Frontend dashboard
├── README.md           # Project documentation
├── CHECKPOINT.md       # Development checkpoints
└── FASTF1_REFERENCE.md # FastF1 API reference info
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- FastF1 library
- Flask

### Backend Setup

1. Navigate to the backend directory
   ```
   cd backend
   ```

2. Install required dependencies
   ```
   pip install -r requirements.txt
   ```

3. Create cache directory for FastF1 data
   ```
   mkdir cache
   ```

4. Run the Flask API server
   ```
   python api.py
   ```

### Frontend Setup

Simply open `index.html` in your web browser after starting the backend server.

## Deployment

### GitHub Setup

1. Create a new GitHub repository
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/f1-dashboard.git
   git push -u origin main
   ```

### Netlify Deployment

1. Log in to Netlify (https://app.netlify.com/)
2. Click "Add new site" → "Import an existing project"
3. Connect to your GitHub repository
4. Configure build settings:
   - Build command: `cd backend && pip install -r requirements.txt`
   - Publish directory: `/`
   - Environment variables:
     - Add `PYTHON_VERSION=3.10`
5. Click "Deploy site"

#### Additional Netlify Configuration

Create a `netlify.toml` file in the project root with:

```toml
[build]
  publish = "/"
  command = "cd backend && pip install -r requirements.txt"

[functions]
  directory = "backend"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

**Note:** For production, you'll need to modify the frontend to use Netlify functions instead of the local Flask API.

## Documentation

- [README.md](README.md) - Project overview
- [CHECKPOINT.md](CHECKPOINT.md) - Development checkpoints
- [FASTF1_REFERENCE.md](FASTF1_REFERENCE.md) - FastF1 API reference

## Development Roadmap

### Phase 1: API Development ✅
- [x] Set up development environment
- [x] Create backend structure
- [x] Implement race calendar fetching
- [x] Create API endpoints for calendar and next race

### Phase 2: Frontend Development ✅
- [x] Design modern UI inspired by F1
- [x] Create responsive dashboard
- [x] Display race calendar with status indicators
- [x] Display next race information

### Phase 3: Enhancements
- [x] Add Sprint format support
- [x] Improve error handling
- [x] Create regression tests
- [ ] Add driver standings
- [ ] Add constructor standings
- [ ] Add track maps

### Phase 4: Deployment ⏳
- [ ] GitHub repository setup
- [ ] Netlify deployment
- [ ] API serverless functions
- [ ] Documentation updates

### Checkpoints
- ✅ **Checkpoint 1 (2025-04-06)**: Initial API implementation
- ✅ **Checkpoint 2 (2025-04-07)**: Frontend dashboard
- 🔄 **Checkpoint 3 (2025-04-07)**: GitHub and Netlify deployment

## License

MIT 