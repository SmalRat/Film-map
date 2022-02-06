import pandas as pd, argparse
import folium


def parsing(list):
    """
    Function for parsing command line

    >>> parsing(["2020", "100", "90", "dataset"])
    (2020, 100.0, 90.0, 'dataset')
    """
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument("year", metavar="Year", type=int, help="Year of films, which will be displayed.")
    parser.add_argument("latitude", metavar="Latitude", type=float, help="Latitude of your point.")
    parser.add_argument("longitude", metavar="Longitude", type=float, help="Longitude of your point.")
    parser.add_argument("path", metavar="Path", help="Path to your dataset.")
    if list:
        results = parser.parse_args(list)
    else:
        results = parser.parse_args()
    return results.year, results.latitude, results.longitude, results.path


def read_csv(path):
    """
    Reads csv file into the pandas dataframe
    """
    data_base = pd.read_csv(path)
    return data_base


"""def geolocation(data_base, year, latitude, longitude):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="Films map")

    from geopy.extra.rate_limiter import RateLimiter
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)

    condition = (data_base['year'] != 0)
    z_valid = z[mask]
    data_base['location'] = data_base[data_base["year"] == year].apply(geocode)
    data_base['point'] = data_base['location'].apply(lambda loc: tuple(loc.point) if loc else None)"""


def creating_map():
    pass

if __name__ == "__main__":
    print(read_csv("data/locations.list"))

