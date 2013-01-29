from datetime import timedelta

from django import template


register = template.Library()

@register.filter
def dt_seconds(value):
    """ Convert and truncate a timedelta to seconds.
    """
    if isinstance(value, timedelta):
        value = value.total_seconds()
    value = int(value)
    return timedelta(seconds=value)