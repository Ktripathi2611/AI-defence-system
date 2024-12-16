from datetime import datetime
import humanize

def format_number(value):
    """Format a number with thousand separators"""
    try:
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value

def time_ago(value):
    """Convert a datetime into a human readable time ago string"""
    if not value:
        return ''
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
            
    now = datetime.now()
    return humanize.naturaltime(now - value)
