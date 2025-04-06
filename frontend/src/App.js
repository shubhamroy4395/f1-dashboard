import React, { useState, useEffect } from 'react';
import './App.css';

// Countdown component
const Countdown = ({ targetDate }) => {
  const [timeLeft, setTimeLeft] = useState({});
  
  useEffect(() => {
    const calculateTimeLeft = () => {
      const difference = new Date(targetDate) - new Date();
      
      if (difference <= 0) {
        return { days: 0, hours: 0, minutes: 0, seconds: 0 };
      }
      
      return {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60)
      };
    };
    
    setTimeLeft(calculateTimeLeft());
    
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);
    
    return () => clearInterval(timer);
  }, [targetDate]);
  
  // Format with leading zeros
  const formatTime = (time) => {
    return time < 10 ? `0${time}` : time;
  };
  
  return (
    <div className="countdown">
      <div className="countdown-item">
        <span className="countdown-value">{timeLeft.days}</span>
        <span className="countdown-label">Days</span>
      </div>
      <div className="countdown-item">
        <span className="countdown-value">{formatTime(timeLeft.hours)}</span>
        <span className="countdown-label">Hours</span>
      </div>
      <div className="countdown-item">
        <span className="countdown-value">{formatTime(timeLeft.minutes)}</span>
        <span className="countdown-label">Minutes</span>
      </div>
      <div className="countdown-item">
        <span className="countdown-value">{formatTime(timeLeft.seconds)}</span>
        <span className="countdown-label">Seconds</span>
      </div>
    </div>
  );
};

function App() {
  const [nextRace, setNextRace] = useState(null);
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'upcoming', 'completed'
  
  // Determine API base URL
  const apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:5000' 
    : '/.netlify/functions/api';
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch next race data
        const nextRaceResponse = await fetch(`${apiBaseUrl}/next-race`);
        if (!nextRaceResponse.ok) {
          throw new Error('Failed to fetch next race data');
        }
        const nextRaceData = await nextRaceResponse.json();
        
        // Fetch calendar data
        const calendarResponse = await fetch(`${apiBaseUrl}/calendar`);
        if (!calendarResponse.ok) {
          throw new Error('Failed to fetch calendar data');
        }
        const calendarData = await calendarResponse.json();
        
        setNextRace(nextRaceData);
        // Make sure calendar data is an array before setting it
        if (calendarData && Array.isArray(calendarData)) {
          setCalendar(calendarData);
        } else if (calendarData && calendarData.races && Array.isArray(calendarData.races)) {
          // Handle case where API returns {races: [...]} format
          setCalendar(calendarData.races);
        } else {
          console.error('Invalid calendar data format:', calendarData);
          setCalendar([]);
          setError('Calendar data has invalid format');
        }
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchData();
  }, [apiBaseUrl]);
  
  // Function to format date for display
  const formatDate = (dateString) => {
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
  };
  
  // Get race status
  const getRaceStatus = (raceDate) => {
    const now = new Date();
    const race = new Date(raceDate);
    
    if (now > race) {
      return 'completed';
    } else if (now.toDateString() === race.toDateString()) {
      return 'ongoing';
    } else {
      return 'upcoming';
    }
  };
  
  // Check if race is next race
  const isNextRace = (round) => {
    return nextRace && nextRace.round === round;
  };
  
  // Ensure calendar is an array before filtering
  const races = Array.isArray(calendar) ? calendar : [];
  
  // Filter races based on selected filter
  const filteredRaces = races.filter(race => {
    if (!race || !race.date) return false;
    
    const status = getRaceStatus(race.date);
    
    if (filter === 'all') return true;
    if (filter === 'upcoming') return status === 'upcoming';
    if (filter === 'completed') return status === 'completed';
    
    return true;
  });

  // Helper function to safely get location data
  const getLocationInfo = (race) => {
    if (!race) return { locality: 'Unknown', country: 'Unknown' };
    
    // Handle different API response formats
    if (race.Circuit && race.Circuit.Location) {
      return {
        locality: race.Circuit.Location.locality || 'Unknown',
        country: race.Circuit.Location.country || 'Unknown'
      };
    } else if (race.location && race.country) {
      return {
        locality: race.location,
        country: race.country
      };
    } else {
      return {
        locality: 'Unknown',
        country: 'Unknown'
      };
    }
  };
  
  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-f">F1</span>
          <span className="logo-text">Dashboard</span>
        </div>
        <div className="season-badge">2023 Season</div>
      </header>
      
      <main className="content">
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <p>Please check your connection and try again.</p>
          </div>
        )}
        
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading race data...</p>
          </div>
        ) : (
          <>
            {nextRace && (
              <section className="next-race-section">
                <h2 className="section-title">Next Race</h2>
                <div className="next-race-card">
                  <div className="next-race-header">
                    <div>
                      <span className="race-round">{nextRace.round}</span>
                      {nextRace.sprint && (
                        <span className="sprint-badge">Sprint</span>
                      )}
                    </div>
                    <span className="race-date">{formatDate(nextRace.date)}</span>
                  </div>
                  <div className="next-race-content">
                    <div>
                      <h3 className="next-race-title">{nextRace.raceName || 'Unknown Race'}</h3>
                      {(() => {
                        const location = getLocationInfo(nextRace);
                        return (
                          <p className="next-race-location">{location.locality}, {location.country}</p>
                        );
                      })()}
                      <p className="next-race-time">Race starts at: {nextRace.time || 'TBD'}</p>
                    </div>
                    
                    <Countdown targetDate={`${nextRace.date}T${nextRace.time || '00:00:00'}`} />
                  </div>
                </div>
              </section>
            )}
            
            <section className="calendar-section">
              <h2 className="section-title">2023 Race Calendar</h2>
              
              {/* Filter controls */}
              <div className="calendar-filters">
                <div className="filter-group">
                  <label>Filter Races</label>
                  <div className="filter-buttons">
                    <button 
                      className={`filter-button ${filter === 'all' ? 'active' : ''}`}
                      onClick={() => setFilter('all')}
                    >
                      All
                    </button>
                    <button 
                      className={`filter-button filter-button-upcoming ${filter === 'upcoming' ? 'active' : ''}`}
                      onClick={() => setFilter('upcoming')}
                    >
                      Upcoming
                    </button>
                    <button 
                      className={`filter-button filter-button-completed ${filter === 'completed' ? 'active' : ''}`}
                      onClick={() => setFilter('completed')}
                    >
                      Completed
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Race list items */}
              <div className="race-list-container">
                {filteredRaces.length > 0 ? (
                  filteredRaces.map((race) => {
                    const status = getRaceStatus(race.date);
                    const isNext = isNextRace(race.round);
                    const location = getLocationInfo(race);
                    
                    return (
                      <div 
                        key={race.round}
                        className={`race-list-item status-${status}`}
                        data-is-next={isNext}
                      >
                        <div className="race-list-round">
                          <div className="round-number">{race.round}</div>
                          {race.sprint && <div className="sprint-flag">S</div>}
                        </div>
                        
                        <div className="race-list-content">
                          <div className="race-list-primary">
                            <h3 className="race-list-title">{race.raceName || 'Unknown Race'}</h3>
                            <p className="race-list-location">{location.locality}, {location.country}</p>
                          </div>
                          
                          <div className="race-list-secondary">
                            <div className="race-list-date">{formatDate(race.date)}</div>
                            <div className={`race-list-status status-status-${status}`}>
                              <span className="status-dot"></span>
                              <span>{status}</span>
                            </div>
                          </div>
                        </div>
                        
                        {isNext && (
                          <div className="next-race-indicator">Next</div>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="no-races-message">
                    {filter !== 'all' ? 'No races match the selected filter.' : 'No race data available.'}
                  </div>
                )}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
