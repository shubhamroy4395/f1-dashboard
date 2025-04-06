import { render, screen } from '@testing-library/react';
import App from './App';

// Mock fetch before tests
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({
      lastUpdated: '2025-04-06T00:00:00Z',
      races: []
    })
  })
);

describe('F1 Dashboard', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders header with title', async () => {
    render(<App />);
    expect(screen.getByText(/F1 Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/2025 Season/i)).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    render(<App />);
    expect(screen.getByText(/Loading F1 data/i)).toBeInTheDocument();
  });
});
