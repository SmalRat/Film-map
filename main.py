"""
Module, which reads data from a file with a films list, determines films,
made in the given year, and geolocation of their production places.
Then finds 10 or fewer such nearest to the given point places, makes markers
for them, and creates a map with a  layer of that markers.
Also, there is another layer, which contains markers
of films shoot in Ukraine.
"""


import argparse
import random
import warnings
import pandas as pd
import folium
# from logging import DEBUG, debug, getLogger
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy import distance
from geopy.exc import GeocoderUnavailable


warnings.simplefilter(action='ignore')
# getLogger().setLevel(DEBUG)


def crop_address(place):
    """
    Crops address and returns new variant
    >>> crop_address("Jo's Cafe* San Marcos* Texas* USA")
    ' San Marcos* Texas* USA'
    >>> crop_address("San Marcos* Texas* USA")
    ' Texas* USA'
    >>> crop_address(" Texas* USA")
    ' USA'
    """

    place = place.split("*")
    place = "*".join(place[1:])

    return place


def memoize_and_write(func, places_dict):
    """
    Decorator for memoization
    """

    def wrapper(place):
        """
        Wrapper. Organises the cache usage and its creation.
        """
        try:
            place = str(place)
            original_place = place

            while True:
                if place not in places_dict.keys() and place != "nan":
                    coordinates = func(place.replace("*", ""))

                    if coordinates:
                        coordinates = tuple([coordinates.point[0], coordinates.point[1]])
                        places_dict[original_place] = coordinates
                        with open("data/places_database.csv", mode="a", encoding="utf-8") as file:
                            file.write(original_place + "," + str(coordinates) + "\n")
                        # debug(str(coordinates) + " returned")
                        return coordinates
                    else:
                        if len(place.split("*")) > 1:
                            # debug(place + "just have been cropped")
                            place = crop_address(place)
                        else:
                            places_dict[original_place] = coordinates
                            with open("data/places_database.csv", mode="a", encoding="utf-8")\
                                    as file:
                                file.write(original_place + "," + str(coordinates) + "\n")
                            # debug(str(coordinates) + " returned for " + original_place)
                            return coordinates
                elif place == "nan":
                    # debug("none returned")
                    return None
                else:
                    raw_coordinates = places_dict[place]
                    if isinstance(raw_coordinates, tuple):
                        # debug(str(raw_coordinates) + " returned")
                        return raw_coordinates
                    try:
                        try:
                            coordinates = tuple(
                                [float(i) for i in tuple(raw_coordinates[1:\
                                len(raw_coordinates) - 1].split(", "))])
                            # debug(str(coordinates) + " returned")
                            return coordinates
                        except ValueError:
                            # debug(raw_coordinates + " caused ValueError")
                            return None
                    except:
                        # debug(raw_coordinates)
                        # debug(" caused other error")
                        return None
        except GeocoderUnavailable:
            print("GeocoderUnavailable error for this location:" + place + ". Proceeding...")
            return None

    return wrapper


def parsing(lst=None):
    """
    Function for parsing command line

    >>> parsing(["2020", "80", "90", "dataset"])
    (2020, 80.0, 90.0, 'dataset')
    """
    parser = argparse.ArgumentParser(description="""Module, which reads data from a file\
     with a films list, determines films, \
     made in the given year, and geolocation of their production places.
    Then finds 10 or fewer such nearest to the given point places, makes markers \
    for them, and creates a map with a  layer of that markers.
    Also, there is another layer, which contains markers\
     of film shooting places in Ukraine.
    You should enter the year of the films' production, the coordinates of the needed point,\
     in comparison to which\
      nearest films will be displayed (lat, lon), and the path to the dataset with your films.""")
    parser.add_argument("year", metavar="Year", type=int, help="Year of films, which\
     will be displayed.")
    parser.add_argument("latitude", metavar="Latitude", type=float, \
                        help="Latitude of your point.")
    parser.add_argument("longitude", metavar="Longitude", type=float,\
                        help="Longitude of your point.")
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


def read_csv():
    """
    Reads csv file (path) into the pandas dataframe.
    Also tries to open data/places_database.csv cache file
    and store info from that file into the dictionary.
    """

    data_base = pd.read_csv("data/processed_locations_list(full).csv", dtype={'year': int})
    places_dict = {}

    try:
        with open("data/places_database.csv", encoding="utf-8") as file:
            print("Cache file found...")
            for line in file:
                line = line.strip("\n")
                coma_pos = line.find(",")
                if coma_pos != -1:
                    places_dict[line[:coma_pos]] = line[coma_pos + 1:]
    except FileNotFoundError:
        print("Haven't found cache file, the new one will be created...")

    return data_base, places_dict


def geolocation(data_base, year, latitude, longitude, geofunc):
    """
    Function for geolocating points from database and calculating distance from them to
    the given user point.

    >>> 33.5 <= geolocation(pd.DataFrame([["Film1", 2020, "Some info",\
     "Los Angeles California USA"]], columns \
    = ["name", "year", "addinfo", "place"]), 2020, 30, 30,\
     memoize_and_write(RateLimiter(Nominatim(user_agent="Films map").geocode), {})).iloc[0, 4][0]\
      <= 34.5 and -118.5 <= geolocation(pd.DataFrame([["Film1", 2020,\
       "Some info", "Los Angeles California USA"]], columns \
    = ["name", "year", "addinfo", "place"]), 2020, 30, 30,\
     memoize_and_write(RateLimiter(Nominatim(user_agent="Films map").geocode),\
      {})).iloc[0, 4][1] <= -117.5
    True
    """
    valid_films = data_base[data_base['year'] == year]
    valid_films["points"] = valid_films['place'].apply(geofunc)
    valid_films["distance_to_the_current_point"] = 0

    for i in range(len(valid_films["points"])):
        point = valid_films.iloc[i, 4]
        if point is not None:
            valid_films.iloc[i, 5] = distance.distance(point, (latitude, longitude)).miles
        else:
            valid_films.iloc[i, 5] = 10**5

    return valid_films


def creating_map(data_base, latitude, longitude, full_data_base, geofunc):
    """
    Creates html file containing map with nearest films as second layer
    and films with scenes made in Ukraine as the third.
    """

    def nearest_points(db):
        """
        Extracts from pandas DataFrame a part with the nearest 10 or fewer films to a given point.
        """
        new_db = pd.DataFrame([])
        for i in range(min(len(db), 10)):
            idx = db["distance_to_the_current_point"].idxmin()
            new_db[i] = db.loc[idx, :]
            if i > 0 and new_db[i]["distance_to_the_current_point"] == new_db[i - 1]\
                    ["distance_to_the_current_point"]:
                new_db[i]["points"] = (new_db[i]["points"][0] +\
                                       random.random() / 100, new_db[i]["points"][1] + \
                                       random.random() / 100)
            db = db.drop(idx)
        new_db = new_db.T

        return new_db

    def nearest_films(db):
        """
        Creates feature group containing markers with nearest films.
        """
        fg = folium.FeatureGroup(name="Nearest films")
        db = nearest_points(db)
        if not db.empty:
            for i in range(len(db["points"])):
                if db.iloc[i, 2] == "NO DATA":
                    html = """<body>
                                    <h4>{}</h4>
                                    Year: {}<br>
                                    <a href="https://www.google.com/search?q=%22{}%22"\
                                    target="_blank">{}</a>
                                    </body>
                                    """
                    html_format = html.format(db.iloc[i, 0], db.iloc[i, 1], db.iloc[i, 0], \
                                              db.iloc[i, 0])
                else:
                    html = """<body>
                                    <h4>{}</h4>
                                    Year: {}<br>
                                    Additional info: {}
                                    <a href="https://www.google.com/search?q=%22{}%22"\
                                    target="_blank">{}</a>
                                    </body>
                                    """
                    html_format = html.format(db.iloc[i, 0], db.iloc[i, 1], db.iloc[i, 2], \
                                              db.iloc[i, 0], db.iloc[i, 0])

                iframe = folium.IFrame(html=html_format,
                                       width=200,
                                       height=100)
                point = db.iloc[i, 4]
                if point:
                    lat = point[0]
                    lon = point[1]
                    fg.add_child(folium.Marker(location=[lat, lon],
                                               popup=folium.Popup(iframe),
                                               icon=folium.Icon(color="red")))
        return fg

    def ukr_films(db):
        """
        Creates feature group containing markers with Ukrainian films.
        """
        ukr_films_db = db[db['place'].str.contains("Ukraine", na=False)]
        ukr_fg = folium.FeatureGroup(name="Films shoot in Ukraine")
        ukr_films_db["points"] = ukr_films_db['place'].apply(geofunc)

        if not ukr_films_db.empty:
            for i in range(len(ukr_films_db["name"])):
                if ukr_films_db.iloc[i, 2] == "NO DATA":
                    html = """<body>
                                    <h4>{}</h4>
                                    Year: {}<br>
                                    <a href="https://www.google.com/search?q=%22{}\
                                    %22"target="_blank">{}</a>
                                    </body>
                                    """
                    html_format = html.format(ukr_films_db.iloc[i, 0], \
                                              ukr_films_db.iloc[i, 1], ukr_films_db.iloc[i, 0], \
                                              ukr_films_db.iloc[i, 0])
                else:
                    html = """<body>
                                    <h4>{}</h4>
                                    Year: {}<br>
                                    Additional info: {}
                                    <a href="https://www.google.com/search?q\
                                    =%22{}%22"target="_blank">{}</a>
                                    </body>
                                    """
                    html_format = html.format(ukr_films_db.iloc[i, 0],\
                                              ukr_films_db.iloc[i, 1], ukr_films_db.iloc[i, 2], \
                                              ukr_films_db.iloc[i, 0], ukr_films_db.iloc[i, 0])

                iframe = folium.IFrame(html=html_format,
                                       width=200,
                                       height=100)

                point = ukr_films_db.iloc[i, 4]

                if point:
                    lat = point[0]
                    lon = point[1]
                    ukr_fg.add_child(folium.Marker(location=[lat, lon],
                                                   popup=folium.Popup(iframe),
                                                   icon=folium.Icon(color="blue")))

        return ukr_fg

    check = False
    try:
        films_map = folium.Map(location=[latitude, longitude],
                         zoom_start=3)
        check = True
    except:
        print("Wrong coordinates!")
    if check:

        print("Creating markers of nearest films layer...")
        fg = nearest_films(data_base)
        print("Creating markers of ukrainian films layer...")
        ukr_fg = ukr_films(full_data_base)

        films_map.add_child(ukr_fg)
        films_map.add_child(fg)
        films_map.add_child(folium.LayerControl())

        print("Saving map...")
        films_map.save('Films_map.html')


def main():
    """
    Main function
    """
    pars_res = parsing()
    import data_processing
    try:
        data_processing.main(pars_res[3])  # processing data in the given file into\
        # the appropriate format and writting it to the data/processed_locations_list(full).csv
        read_results = read_csv()

        geolocator = Nominatim(user_agent="Films map")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.3, max_retries=2,\
                              swallow_exceptions=True, \
                              return_value_on_exception=None, error_wait_seconds=2)
        geocode_modified = memoize_and_write(geocode, read_results[1])
        print("Starting to search the geolocations...")
        db = geolocation(read_results[0], pars_res[0], pars_res[1], pars_res[2], geocode_modified)
        print("All posible geolocations found. Creating map...")
        creating_map(db, pars_res[1], pars_res[2], read_results[0], geocode_modified)
        print("Success, look at Films_map.html!")
    except FileNotFoundError:
        print("Failure: haven't found the file specified!")


if __name__ == "__main__":
    main()
