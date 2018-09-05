from math import cos, pi


def lat_degrees_from_miles(miles):
    return miles / 69  # each degree latitude is approx. 69 miles


def long_degrees_from_miles_at_lat(miles, lat):
    # each degree longitude is approx. 69 miles at the equator
    # but gets closer to 0 as a function of the cosine of latitude
    # the closer the latitude is to the poles
    return cos(lat * pi / 180) * miles / 69


def get_weekday_span_between(weekday1, weekday2):
    weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    weekday1_index = weekdays.index(weekday1)
    weekday2_index = weekdays.index(weekday2)

    if weekday1_index == weekday2_index:
        return [weekday1]
    elif weekday1_index < weekday2_index:
        return weekdays[weekday1_index:weekday2_index + 1]
    else:
        return weekdays[weekday1_index:] + weekdays[:weekday2_index + 1]