import pandas as pd, argparse
import folium
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


def parsing(lst=None):
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
    if lst:
        results = parser.parse_args(lst)
    else:
        results = parser.parse_args()
    return results.year, results.latitude, results.longitude, results.path


def read_csv(path):
    """
    Reads csv file into the pandas dataframe
    """
    data_base = pd.read_csv(path)
    return data_base


def geolocation(data_base, yearб latitude, longitude):
    geolocator = Nominatim(user_agent="Films map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)
    condition = (data_base['year'] == year)
    valid_films = data_base[condition]
    location_series = valid_films['place'].apply(geocode)
    point_series = location_series.apply(lambda loc: tuple([loc.point[0], loc.point[1]]) if loc else None)
    valid_films["points"] = point_series

    return valid_films


def creating_map(data_base, year, latitude, longitude):
    check = False
    try:
        map = folium.Map(location=[latitude, longitude],
                     zoom_start=3)
        check = True
    except:
        print("Wrong coordinates!")
    if check:
        fg = folium.FeatureGroup(name="Nearest films")
        for point in data_base["points"]:
            if point:
                lat = point[0]
                lon = point[1]
                fg.add_child(folium.Marker(location=[lat, lon],
                                           popup=folium.Popup("Film"),
                                           icon=folium.Icon(color="red")))
        map.add_child(fg)
        map.save('Map_5.html')


def main():
    pars_res = parsing(["2010", "100", "90", "data/shortened_and_processed_locations_list(3000 lines)"])
    db = geolocation(read_csv(pars_res[3]), pars_res[0])
    creating_map(db, pars_res[0], pars_res[1], pars_res[2])

if __name__ == "__main__":
    main()

    #print(read_csv("data/shortened_and_processed_locations_list(3000 lines)")["place"])

