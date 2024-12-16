from datetime import datetime

def format_number(value):
    """Format a number with thousand separators"""
    try:
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value

def time_ago(dt):
    """Convert a datetime into a human-readable relative time string."""
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return 'just now'
    
    minutes = int(seconds / 60)
    if minutes < 60:
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    
    hours = int(minutes / 60)
    if hours < 24:
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    
    days = int(hours / 24)
    if days < 7:
        return f'{days} day{"s" if days != 1 else ""} ago'
    
    weeks = int(days / 7)
    if weeks < 4:
        return f'{weeks} week{"s" if weeks != 1 else ""} ago'
    
    months = int(days / 30)
    if months < 12:
        return f'{months} month{"s" if months != 1 else ""} ago'
    
    years = int(days / 365)
    return f'{years} year{"s" if years != 1 else ""} ago'
