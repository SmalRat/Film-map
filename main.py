import pandas as pd, argparse
import folium
import random
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy import distance


def parsing(lst=None):
    """
    Function for parsing command line

    >>> parsing(["2020", "80", "90", "dataset"])
    (2020, 80.0, 90.0, 'dataset')
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
    universal_message = ", please check your coordinates"
    if not -90 <= results.latitude <= 90:
        message = "%r not in range [-90, 90]" % (results.latitude,)
        raise argparse.ArgumentTypeError(message + universal_message)
    if not -90 <= results.longitude <= 90:
        message = "%r not in range [-90, 90]" % (results.longitude,)
        raise argparse.ArgumentTypeError(message + universal_message)
    return results.year, results.latitude, results.longitude, results.path


def read_csv(path):
    """
    Reads csv file into the pandas dataframe
    """
    data_base = pd.read_csv(path)
    return data_base


def geolocation(data_base, year, latitude, longitude):
    geolocator = Nominatim(user_agent="Films map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)
    condition = (data_base['year'] == year)
    valid_films = data_base[condition]
    location_series = valid_films['place'].apply(geocode)
    point_series = location_series.apply(lambda loc: tuple([loc.point[0], loc.point[1]]) if loc else None)
    valid_films["points"] = point_series
    valid_films["distance_to_the_current_point"] = 0
    for i in range(len(valid_films["points"])):
        point = valid_films.iloc[i, 4]
        valid_films.iloc[i, 5] = distance.distance(point, (latitude, longitude)).miles
    print(valid_films)
    return valid_films


def creating_map(data_base, year, latitude, longitude):
    def nearest_points(db):
        new_db = pd.DataFrame([])
        for i in range(min(len(db), 10)):
            idx = db["distance_to_the_current_point"].idxmin()
            new_db[i] = db.loc[idx, :]
            if i > 0 and new_db[i]["distance_to_the_current_point"]  == new_db[i-1]["distance_to_the_current_point"]:
                new_db[i]["points"] = (new_db[i]["points"][0] + random.random()/100, new_db[i]["points"][1] +\
                                       random.random()/100)
            db.drop(idx)
        new_db = new_db.T
        return new_db
    check = False
    try:
        map = folium.Map(location=[latitude, longitude],
                     zoom_start=3)
        check = True
    except:
        print("Wrong coordinates!")
    if check:
        fg = folium.FeatureGroup(name="Nearest films")
        data_base = nearest_points(data_base)
        print(data_base)
        for point in data_base["points"]:
            if point:
                lat = point[0]
                lon = point[1]
                fg.add_child(folium.Marker(location=[lat, lon],
                                           popup=folium.Popup("Film"),
                                           icon=folium.Icon(color="red")))
        map.add_child(fg)
        map.save('Films_map.html')


def main():
    pars_res = parsing(["2010", "80.2323", "23.67", "data/shortened_and_processed_locations_list(3000 lines)"])
    db = geolocation(read_csv(pars_res[3]), pars_res[0], pars_res[1], pars_res[2])
    creating_map(db, pars_res[0], pars_res[1], pars_res[2])

if __name__ == "__main__":
    main()

