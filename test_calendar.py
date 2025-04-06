import requests
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()

# Default to 2025 season
DEFAULT_F1_YEAR = 2025

def fetch_f1_calendar(year=DEFAULT_F1_YEAR):
    """Fetch F1 calendar data from our API"""
    try:
        url = f'http://localhost:5001/api/calendar/{year}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[bold red]Error fetching calendar:[/bold red] {str(e)}")
        return []

def fetch_next_race():
    """Fetch information about the next race from our API"""
    try:
        url = 'http://localhost:5001/api/next-race'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[bold red]Error fetching next race:[/bold red] {str(e)}")
        return None

def display_calendar(calendar_data):
    """Display calendar data in a formatted table"""
    if not calendar_data:
        console.print("[yellow]No calendar data available[/yellow]")
        return
    
    # Create a table
    table = Table(title=f"F1 Calendar for {calendar_data[0]['date'][:4]}")
    table.add_column("Round", justify="center", style="cyan")
    table.add_column("Grand Prix", style="magenta")
    table.add_column("Circuit", style="green")
    table.add_column("Date", justify="center", style="yellow")
    table.add_column("Format", justify="center", style="blue")
    table.add_column("Status", justify="center", style="red")
    
    # Add rows
    for race in calendar_data:
        # Skip testing events
        if race['format'] == 'testing':
            continue
            
        # Format status with colors
        if race['status'] == 'completed':
            status = "[dim]COMPLETED[/dim]"
        elif race['status'] == 'in_progress':
            status = "[bold green]IN PROGRESS[/bold green]"
        else:
            status = "[bold yellow]UPCOMING[/bold yellow]"
        
        # Format event type
        if race.get('is_sprint_weekend', False) or 'sprint' in str(race['format']).lower():
            format_type = "[bold blue]SPRINT[/bold blue]"
        else:
            format_type = "REGULAR"
        
        table.add_row(
            str(race['round']),
            race['name'],
            f"{race['circuit']} ({race['country']})",
            race['date'],
            format_type,
            status
        )
    
    # Display the table
    console.print(table)

def display_next_race(race_data):
    """Display detailed information about the next race"""
    if not race_data:
        console.print("[yellow]No upcoming race information available[/yellow]")
        return
    
    # Determine if it's a sprint weekend
    is_sprint = race_data.get('is_sprint_weekend', False) or 'sprint' in str(race_data['format']).lower()
    
    console.print("\n[bold blue]Next F1 Race:[/bold blue]")
    console.print(f"[bold magenta]{race_data['name']}[/bold magenta]")
    console.print(f"Round: [cyan]{race_data['round']}[/cyan]")
    console.print(f"Circuit: [green]{race_data['circuit']} ({race_data['country']})[/green]")
    console.print(f"Date: [yellow]{race_data['date']}[/yellow]")
    console.print(f"Format: [blue]{'SPRINT WEEKEND' if is_sprint else 'REGULAR WEEKEND'}[/blue]")
    
    # Display session times if available
    console.print("\n[bold white]Session Schedule:[/bold white]")
    for session, time in race_data['session_dates'].items():
        if time:
            # Highlight sprint session if available
            if session == 'sprint' and is_sprint:
                console.print(f"{session.upper()}: [bold cyan]{time}[/bold cyan]")
            else:
                console.print(f"{session.upper()}: [cyan]{time}[/cyan]")

def display_sprint_races(calendar_data):
    """Display all sprint races in the season"""
    if not calendar_data:
        console.print("[yellow]No calendar data available[/yellow]")
        return
    
    # Filter for sprint events
    sprint_races = [race for race in calendar_data if 
                   race.get('is_sprint_weekend', False) or 'sprint' in str(race['format']).lower()]
    
    if not sprint_races:
        console.print("[yellow]No sprint races found in the calendar[/yellow]")
        return
    
    # Create a table for sprint races
    table = Table(title=f"Sprint Races for {calendar_data[0]['date'][:4]}")
    table.add_column("Round", justify="center", style="cyan")
    table.add_column("Grand Prix", style="magenta")
    table.add_column("Circuit", style="green")
    table.add_column("Date", justify="center", style="yellow")
    table.add_column("Sprint Time", justify="center", style="blue")
    
    # Add rows
    for race in sprint_races:
        sprint_time = race['session_dates'].get('sprint', 'Not available')
        
        table.add_row(
            str(race['round']),
            race['name'],
            f"{race['circuit']} ({race['country']})",
            race['date'],
            sprint_time or "Not available"
        )
    
    # Display the table
    console.print(table)

if __name__ == "__main__":
    console.print("[bold]F1 Dashboard Calendar Test[/bold]")
    
    # Fetch and display calendar for 2025 season
    console.print(f"\nFetching calendar for {DEFAULT_F1_YEAR}...")
    calendar = fetch_f1_calendar()
    display_calendar(calendar)
    
    # Display sprint races
    console.print("\n[bold]Sprint Races:[/bold]")
    display_sprint_races(calendar)
    
    # Fetch and display next race information
    console.print("\nFetching next race information...")
    next_race = fetch_next_race()
    display_next_race(next_race) 