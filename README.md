# F1 Dashboard

A real-time Formula 1 dashboard displaying race calendars, upcoming events, and race information using the FastF1 API.

## Features

- 📅 Complete 2025 F1 race calendar
- 🏎️ Next race information with countdown
- 🏁 Race weekend session schedules
- 🔄 Sprint weekend detection
- 💻 Modern, responsive UI inspired by F1's design language

## Project Structure

```
F1Dashboard/
├── backend/               # Flask API server
│   ├── app.py             # Main Flask application
│   ├── api_handler.py     # Serverless function handler
│   ├── race_calendar_fetcher.py  # F1 data processor
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend application
│   ├── public/            # Static assets
│   └── src/               # React components and styling
└── README.md              # This file
```

## UI Framework & Design Language

The F1 Dashboard uses the following UI framework and design principles:

### Framework

- **React**: Modern component-based UI library for building interactive user interfaces
- **CSS3**: Custom styling with modern CSS features (Grid, Flexbox, Variables, Animations)
- **Responsive Design**: Mobile-first approach with adaptive layouts for all devices

### Design Language

- **F1 Racing Aesthetic**: 
  - Sleek, high-performance interface inspired by F1 car designs
  - Dynamic elements with subtle animations to convey speed and precision
  - Aerodynamic card layouts with strategic use of negative space

- **Color Palette**:
  - Primary: F1 Red (#e10600) - Used for highlights, actions, and key elements
  - Background: Dark theme (#15151e) with gradient overlays for depth
  - Accents: Sprint yellow (#ff7d00), Live green (#39e600), Upcoming yellow (#ffcc00)
  - Text: White (#ffffff) and carefully balanced gray variants for hierarchy

- **Typography**:
  - Font Family: Titillium Web (primary) - Used in official F1 materials
  - Racing-inspired text treatments with uppercase for headers
  - Precise letter spacing and line heights for maximum readability
  - Clear information hierarchy with distinct size and weight differences

- **Components**:
  - Aerodynamic card designs with strategic border highlights
  - Semi-transparent surfaces with backdrop blur for depth
  - Contextual color indicators for race status (upcoming, live, completed)
  - Animated elements that respond to user interaction
  - Pulse animations for live race indicators

- **Motion Design**:
  - Subtle entrance animations for page elements
  - Precise timing functions mimicking F1 acceleration curves
  - Interactive hover states with transform properties
  - Loading animations inspired by F1 starting lights
  - Status indicators with pulse animations for live events

### UI Improvement Roadmap

For future UI enhancements:

1. **Component Library Integration**
   - Consider Material-UI or Chakra UI for consistent component behavior
   - Implement theming with easy customization options
   - Develop reusable F1-themed components for rapid development

2. **Advanced Data Visualization**
   - Interactive circuit maps with race progression
   - Real-time telemetry data visualization for active races
   - Comparative driver/team performance charts
   - Weather impact visualizations for race conditions

3. **Animation & Transitions**
   - Page transitions with racing-inspired animations
   - Parallax scrolling effects for background elements
   - 3D transformations for featured content
   - Micro-interactions that enhance usability

4. **Accessibility Improvements**
   - Enhanced color contrast while maintaining F1 aesthetic
   - Keyboard navigation with visible focus states
   - Screen reader optimizations with aria attributes
   - Reduced motion options for users with vestibular disorders

## Running the Application

### Prerequisites

- Node.js (v18+)
- Python (v3.9+)
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create cache directory
mkdir -p cache

# Run the Flask server
python app.py
```

The backend API will be available at `http://localhost:5000`.

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend development server will be available at `http://localhost:3000`.

### PowerShell Command Notes

Due to PowerShell syntax differences, use semicolons instead of && for command chaining:

```powershell
# Running the backend server in PowerShell
cd E:\F1Dashboard\backend; python app.py

# Running the frontend in PowerShell
cd E:\F1Dashboard\frontend; npm start
```

## Deployment

The project is configured for deployment on Netlify. See detailed instructions in the deployment section.

## Common Issues and Solutions

1. **PowerShell Command Syntax**
   - PowerShell does not support the `&&` operator like bash. Use semicolons instead.
   - Example: `cd path/to/dir; command` instead of `cd path/to/dir && command`

2. **FastF1 API Cache Issues**
   - Ensure the `cache` directory exists in the backend folder
   - Check permissions if you encounter write access errors

3. **API Connection Issues**
   - Verify the API base URL in the frontend code matches your backend
   - For local development, ensure CORS is properly configured

## License

This project is licensed under the MIT License - see the LICENSE file for details. 