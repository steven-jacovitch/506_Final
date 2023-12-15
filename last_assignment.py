import copy
import five_oh_six as utl

from pathlib import Path


# Constants
CACHE_FILEPATH = "./CACHE.json"
NONE_VALUES = ("", "n/a", "none", "unknown")
SWAPI_ENDPOINT = "https://swapi.py4e.com/api"
SWAPI_CATEGORES = f"{SWAPI_ENDPOINT}/"
SWAPI_PEOPLE = f"{SWAPI_ENDPOINT}/people/"
SWAPI_PLANETS = f"{SWAPI_ENDPOINT}/planets/"
SWAPI_SPECIES = f"{SWAPI_ENDPOINT}/species/"
SWAPI_STARSHIPS = f"{SWAPI_ENDPOINT}/starships/"

# Create/retrieve cache
cache = utl.create_cache(CACHE_FILEPATH)


def assign_crew_members(crew_size, crew_positions, personnel):
    """Returns a dictionary of crew members mapped (i.e., assigned) by position and limited in
    size by the < crew_size > value.

    The < crew_positions > and < personnel > tuples must contain the same number of elements. The
    individual < crew_positions > and < personnel > elements are then paired by index position and
    stored in a dictionary structured as follows:

    {< crew_position[0] >: < personnel[0] >, < crew_position[1] >: < personnel[1] >, ...}

    WARN: The number of crew positions/members is limited by the < crew size > value. No additional
    crew positions/members are permitted to be assigned to the crew members dictionary even if
    passed to the function. Crew positions/members are assigned to the dictionary as key-value pairs
    by index position (0, 1, ...).

    A single line dictionary comprehension is employed to create the new crew members dictionary.

    Parameters:
        crew_size (int): max crew members permitted
        crew_positions (tuple): crew positions (e.g., 'pilot', 'copilot', etc.)
        personnel (tuple): flight crew to be assigned to the crew positions

    Returns:
        dict: crew members by position
    """

    return {crew_positions[i]: personnel[i] for i in range(crew_size)}


def board_passengers(max_passengers, passengers):
    """Returns a list of passengers that are permitted to board a starship or other vehicle. The
    size of the list is governed by the < max_passengers > value.

    WARN: The number of passengers permitted to board a starship or other vehicle is limited by the
    provided < max_passengers > value. If the number of passengers attempting to board exceeds
    < max_passengers > only the first < n > passengers (where `n` = "max_passengers") are permitted
    to board the vessel.

    Parameters:
        max_passengers (int): max number of passengers permitted to board a vessel
        passengers (list): passengers seeking permission to board

    Returns:
        list: passengers to board
    """

    return passengers[:max_passengers]


def calculate_articles_mean_word_count(articles):
    """Calculates the mean (e.g., average) "word_count" of the passed in list of < articles >.
    Excludes from the calculation any article with a word count of zero (0) or < None >. Word counts
    are summed and then divided by the number of non-zero/non-< None > "word_count" articles. The
    resulting mean value is rounded to the second (2nd) decimal place and returned to the caller.

    The function maintains a count of the number of articles evaluated and a count of the total
    words accumulated from each article's "word_count" key-value pair.

    The function checks the truth value of each article's "word_count" before attempting to
    increment the count. If the truth vallue of the "word_count" is < False > the article is
    excluded from the count.

    Parameters:
        articles (list): nested dictionary representations of New York Times articles

    Returns:
        float: mean word count rounded to the second (2nd) decimal place
    """

    word_count_sum = 0
    article_count = 0
    for article in articles:
        if article["word_count"] and article["word_count"] > 0:
            article_count += 1
            word_count_sum += article["word_count"]
    return round(word_count_sum / article_count, 2)


def convert_episode_values(episodes, none_values):
    """Converts select string values to either < int >, < float >, < list >, or < None >
    in the passed in list of nested dictionaries. The function delegates to the
    < utl.to_*() > functions the task of converting the specified strings to either
    an integer, float, list, or None.

    If a value is a member of < none_values > the value is replaced by < None >. Otherwise,
    various < utl.to_*() > functions are called as necessary in an attempt to convert
    certain episode values to more appropriate types per the "Type conversions" listed below.

    Type conversions:
        series_season_num (str) -> series_season_num (int | None)
        series_episode_num (str) -> series_episode_num (int | None)
        season_episode_num (str) -> season_episode_num (int | None)
        episode_prod_code (str) -> episode_prod_code (float | None)
        episode_us_viewers_mm (str) -> episode_us_viewers_mm (float | None)
        episode_writers (str) -> episode_writers (list | None)

    Parameters:
        episodes (list): nested episode dictionaries
        none_values (tuple): strings to convert to None

    Returns:
        list: nested episode dictionaries containing mutated key-value pairs
    """

    for episode in episodes:
        for key, value in episode.items():
            if value in none_values:
                episode[key] = None
            elif key == "series_season_num":
                episode[key] = utl.to_int(value)
            elif key == "series_episode_num":
                episode[key] = utl.to_int(value)
            elif key == "season_episode_num":
                episode[key] = utl.to_int(value)
            elif key == "episode_prod_code":
                episode[key] = utl.to_float(value)
            elif key == "episode_us_viewers_mm":
                episode[key] = utl.to_float(value)
            elif key == "episode_writers":
                episode[key] = utl.to_list(value, ", ")
    return episodes


def count_episodes_by_director(episodes):
    """Constructs and returns a dictionary of key-value pairs that associate each director with
    a count of the episodes that they directed. The director's name comprises the key and the
    associated value a count of the number of episodes they directed. Duplicate keys are NOT
    permitted.

    Format:
        {
            < director_name_01 >: < episode_count >,
            < director_name_02 >: < episode_count >,
            ...
        }

    Each director's episode count is incremented by < 1.0 > if, and only if, the director is
    the only person credited with directing the episode. Otherwise, if more than one person
    is credited with directing the episode each director is allocated a fraction of < 1.0 >.
    This value is calculated by dividing < 1.0 > by the number of directors credited with
    directing the episode.

    Parameters:
        episodes (list): nested episode dictionaries

    Returns:
        dict: a dictionary that store counts of the number of episodes directed
              by each director
    """

    director_episode_counts = {}
    for episode in episodes:
        directors = episode["episode_director"].split(", ")
        increment = 1.0 / len(directors)
        for director in directors:
            if director in director_episode_counts:
                director_episode_counts[director] += increment
            else:
                director_episode_counts[director] = increment
    return director_episode_counts


def get_most_viewed_episode(episodes):
    """Identifies and returns a list of one or more episodes with the highest recorded
    viewership. Ignores episodes with no viewship value. Includes in the list only those
    episodes that tie for the highest recorded viewership. If no ties exist only one
    episode will be returned in the list. Delegates to the function < has_viewer_data >
    the task of determining if the episode includes viewership "episode_us_viewers_mm"
    numeric data.

    Parameters:
        episodes (list): nested episode dictionaries

    Returns:
        list: episode(s) with the highest recorded viewership.
    """

    viewer_count = 0
    top_episodes = []
    for episode in episodes:
        if has_viewer_data(episode):
            if episode["episode_us_viewers_mm"] > viewer_count:
                viewer_count = episode["episode_us_viewers_mm"]
                top_episodes = [episode]
            elif episode["episode_us_viewers_mm"] == viewer_count:
                top_episodes.append(episode)
    return top_episodes


def get_news_desks(articles, none_values):
    """Returns a list of New York Times news desks sourced from the passed in
    < articles > list. Accesses the news desk name from each article's "news_desk"
    key-value pair. Filters out duplicates in order to guarantee uniqueness. The
    list sorted alphanumerically before being returned to the caller.

    Delegates to the function < utl.to_none > the task of converting "news_desk"
    values that equal "None" (a string) to None. Only news_desk values that are "truthy"
    (i.e., not None) are returned in the list.

    Parameters:
        articles (list): nested dictionary representations of New York Times articles
        none_values (tuple): strings to convert to None

    Returns:
        list: news desk strings (no duplicates) sorted alphanumerically
    """

    news_desks = []
    for article in articles:
        news_desk = utl.to_none(article["news_desk"], none_values)
        if news_desk and news_desk not in news_desks:
            news_desks.append(news_desk)
    news_desks.sort()
    return news_desks


def get_swapi_resource(url, params=None, timeout=10):
    """Retrieves a deep copy of a SWAPI resource from either the local < cache >
    dictionary or from a remote API if no local copy exists. Delegates to the function
    < utl.create_cache_key > the task of minting a key that is used to identify a cached
    resource. If the desired resource is not located in the cache, delegates to the
    function < get_resource > the task of retrieving the resource from SWAPI.
    A deep copy of the resource retrieved remotely is then added to the local < cache > by
    mapping it to a new < cache[key] >. The mutated cache is written to the file
    system before a deep copy of the resource is returned to the caller.

    WARN: Deep copying is required to guard against possible mutatation of the cached
    objects when dictionaries representing SWAPI entities (e.g., films, people, planets,
    species, starships, and vehicles) are modified by other processes.

    Parameters:
        url (str): a uniform resource locator that specifies the resource.
        params (dict): optional dictionary of querystring arguments.
        timeout (int): timeout value in seconds

    Returns:
        dict|list: requested resource sourced from either the local cache or a remote API
    """

    key = utl.create_cache_key(url, params)
    if key in cache.keys():
        return copy.deepcopy(cache[key])  # recursive copy of objects
    else:
        resource = utl.get_resource(url, params, timeout)
        cache[key] = copy.deepcopy(resource)  # recursive copy of objects
        utl.write_json(CACHE_FILEPATH, cache)  # persist mutated cache
        return resource


def group_articles_by_news_desk(news_desks, articles):
    """Returns a dictionary of "news desk" key-value pairs that group the passed in
    < articles > by their parent news desk. The passed in < news_desks > list provides
    the keys while each news desk's < articles > are stored in a list and assigned to
    the appropriate "news desk" key. Each key-value pair is structured as follows:

    {
        < news_desk_name_01 >: [{< article_01 >}, {< article_05 >}, ...],
        < news_desk_name_02 >: [{< article_20 >}, {< article_31 >}, ...],
        ...
    }

    Each dictionary that represents an article is a "thinned" version of the New York Times
    original and consists of the following key-value pairs ordered as follows:

    Key order:
        web_url
        headline_main (new name)
        news_desk
        byline_original (new name)
        document_type
        material_type (new name)
        abstract
        word_count
        pub_date

    Parameters:
        news_desks (list): list of news_desk names
        articles (list): nested dictionary representations of New York Times articles

    Returns
        dict: key-value pairs that group articles by their parent news desk
    """

    grouped_articles = {desk: [] for desk in news_desks}
    for article in articles:
        desk = article["news_desk"]
        if desk in grouped_articles:
            thinned_article = {
                "web_url": article["web_url"],
                "headline_main": article["headline"]["main"],
                "news_desk": desk,
                "byline_original": article["byline"]["original"],
                "document_type": article["document_type"],
                "material_type": article["type_of_material"],
                "abstract": article["abstract"],
                "word_count": article["word_count"],
                "pub_date": article["pub_date"],
            }
            grouped_articles[desk].append(thinned_article)
    return grouped_articles


def has_viewer_data(episode):
    """Checks the truth value of an episode's "episode_us_viewers_mm" key-value pair. Returns
    True if the truth value is "truthy" (e.g., numeric values that are not 0, non-empty sequences
    or dictionaries, boolean True); otherwise returns False if a "falsy" value is detected (e.g.,
    empty sequences (including empty or blank strings), 0, 0.0, None, boolean False)).

    Parameters:
        episode (dict): represents an episode

    Returns:
        bool: True if "episode_us_viewers_mm" value is truthy; otherwise False
    """

    if episode["episode_us_viewers_mm"]:
        return True
    else:
        return False


def transform_droid(data, keys, none_values):
    """Returns a new "thinned" dictionary representation of a droid based on the passed in
     < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "droid" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

     * the subset of < data > key-value pairs to be mapped to the new dictionary.
     * the order in which the < data > key-value pairs are mapped to the new dictionary.
     * the key names to be used in the new dictionary. Each key in < keys > corresponds to
       a key in < data >. Each value in < keys > represents the (new) key name to be used
       in the new dictionary.

     < data > values are converted to more appropriate types as outlined below under "Mappings".
     Strings found in < none_values > are converted to < None > irrespective of case. Type
     conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
     corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new key-value
    pair to the new "droid" dictionary.

     Mappings (old key -> new key):
         url (str) -> url (str)
         name (str) -> name (str | None)
         model (str) -> model (str | None)
         manufacturer (str) -> manufacturer (str | None)
         create_year (str) -> create_date (dict | None)
         height (str) -> height_cm (float | None)
         mass (str) -> mass_kg (float | None)
         equipment (str) -> equipment (list | None)
         instructions (str) -> instructions (list | None)

     Parameters:
         data (dict): source data
         keys (dict): old key to new key mappings
         none_values (tuple): strings to convert to None

     Returns:
         dict: new dictionary representation of a droid
    """

    droid = {}
    for old_key, new_key in keys["droid"].items():
        value = data.get(old_key, None)
        if value in none_values:
            value = utl.to_none(value, none_values)
        elif old_key in ["height", "mass"]:
            value = utl.to_float(value)
        elif old_key == "create_year":
            value = utl.to_year_era(value)
        elif old_key in ["equipment", "instructions"]:
            value = utl.to_list(value, "|")
        droid[new_key] = value
    return droid


def transform_person(data, keys, none_values, planets=None):
    """Returns a new "thinned" dictionary representation of a person based on the passed in
    < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "person" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new
    key-value pair to the new "person" dictionary.

    Both the "homeworld" and "species" values require special handling.

    Retrieving a dictionary representation of the person's home planet is delegated to the
    function < get_swapi_resource() >. If the caller passes in a Wookieepedia-sourced
    < planets > list this function delegates to the function < utl.get_nested_dict() > the task
    of retrieving the Wookieepedia representation of the homeworld from < planets >.
    If the homeworld is found in < planets > the SWAPI and Wookieepedia dictionaries are
    combined. Cleaning the homeworld dictionary is delegated to the function < transform_planet() >.

    Likewise, retrieving a representation of the person's species is delegated to the function
    < get_swapi_resource() >. Cleaning the species dictionary is delegated to the function
    < transform_species() >.

    Mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        birth_year (str) -> birth_date (dict | None)
        height (str) -> height_cm (float | None)
        mass (str) -> mass_kg (float | None)
        homeworld (str) -> homeworld (dict | None)
        species (list) -> species (dict | None)
        force_sensitive (str) -> force_sensitive (str | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None
        planets (list): Supplementary planet data

    Returns:
        dict: new dictionary representation of a person
    """

    person = {}
    for old_key, new_key in keys["person"].items():
        value = data.get(old_key, None)
        if value in none_values:
            value = utl.to_none(value, none_values)
        elif old_key in ["height", "mass"]:
            value = utl.to_float(value)
        elif old_key == "birth_year":
            value = utl.to_year_era(value)
        elif old_key == "homeworld":
            value = get_swapi_resource(value)
            if planets:
                wookie_homeworld = utl.get_nested_dict(planets, "name", value["name"])
                if wookie_homeworld:
                    value.update(wookie_homeworld)
            value = transform_planet(value, keys, none_values)
        elif old_key == "species":
            value = get_swapi_resource(value[0])
            value = transform_species(value, keys, none_values)
        person[new_key] = value
    return person


def transform_planet(data, keys, none_values):
    """Returns a new "thinned" dictionary representation of a planet based on the passed in
    < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "planet" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new
    key-value pair to the new "planet" dictionary.

    Mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        region (str) -> region (str | None)
        sector (str) -> sector (str | None)
        suns (str) -> suns (int | None)
        moons (str) -> moons (int | None)
        orbital_period (str) -> orbital_period_days (float | None)
        diameter (str) -> diameter_km (int | None)
        gravity (str) -> gravity_std (float | None)
        climate (str) -> climate (list | None)
        terrain (str) -> terrain (list | None)
        population (str) -> population (int | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None

    Returns:
        dict: new dictionary representation of a planet
    """

    planet = {}
    for old_key, new_key in keys["planet"].items():
        value = data.get(old_key, None)
        if value in none_values:
            value = utl.to_none(value, none_values)
        elif old_key in ["suns", "moons", "diameter", "population"]:
            value = utl.to_int(value)
        elif old_key == "orbital_period":
            value = utl.to_float(value)
        elif old_key == "gravity":
            value = utl.to_gravity_value(value)
        elif old_key in ["climate", "terrain"]:
            value = utl.to_list(value, ", ")
        planet[new_key] = value
    return planet


def transform_species(data, keys, none_values):
    """Returns a new "thinned" dictionary representation of a species based on the passed in
    < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "species" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new
    key-value pair to the new "species" dictionary.

    Mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        classification (str) -> classification (str | None)
        designation (str) -> designation (str | None)
        average_lifespan (str) -> average_lifespan_yrs (int | None)
        average_height (str) -> average_height_cm (float | None)
        language (str) -> language (str | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None

    Returns:
        dict: new dictionary representation of a planet
    """

    species = {}
    for old_key, new_key in keys["species"].items():
        value = data.get(old_key, None)
        if value in none_values:
            value = utl.to_none(value, none_values)
        elif old_key in ["average_height"]:
            value = utl.to_float(value)
        elif old_key == "average_lifespan":
            value = utl.to_int(value)
        species[new_key] = value
    return species


def transform_starship(data, keys, none_values):
    """Returns a new "thinned" dictionary representation of a starship based on the passed in
    < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "starship" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new
    key-value pair to the new "starship" dictionary.

    Assigning crew members and passengers constitute separate operations.

    Mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        model (str) -> model (str | None)
        starship_class (str) -> starship_class (str | None)
        manufacturer (str) -> manufacturer (str | None)
        length (str) -> length_m (float | None)
        hyperdrive_rating (str) -> hyperdrive_rating (float | None)
        MGLT (str) -> max_megalight_hr (int | None)
        max_atmosphering_speed (str) -> max_atmosphering_speed_kph (int | None)
        crew (str) -> crew_size (int | None)
        crew_members (dict) -> crew_members (dict | None)
        passengers (str) -> max_passengers (int | None)
        passengers_on_board (list) -> passengers_on_board (list | None)
        cargo_capacity (str) -> cargo_capacity_kg (int | None)
        consumables (str) -> consumables (str | None)
        armament (list) -> armament (list | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None

    Returns:
        dict: new dictionary representation of a planet
    """

    starship = {}
    for old_key, new_key in keys["starship"].items():
        value = data.get(old_key, None)
        if value in none_values:
            value = utl.to_none(value, none_values)
        elif old_key in ["length", "hyperdrive_rating"]:
            value = utl.to_float(value)
        elif old_key in ["MGLT", "crew", "passengers", "cargo_capacity", "max_atmosphering_speed"]:
            value = utl.to_int(value)
        elif old_key == "armament":
            value = utl.to_list(value, ",")
        starship[new_key] = value
    return starship


def main():
    """Entry point for program.

    Parameters:
        None

    Returns:
        None
    """

    # 3.1 CHALLENGE 01

    assert utl.to_float("4") == 4.0
    assert utl.to_float("506,000,000.9999") == 506000000.9999
    assert utl.to_float("Darth Vader") == "Darth Vader"

    assert utl.to_int("506") == 506
    assert utl.to_int("506,000,000.9999") == 506000000
    assert utl.to_int("Ahsoka Tano") == "Ahsoka Tano"

    # 3.2 CHALLENGE 02

    assert utl.to_list("Use the Force") == ["Use", "the", "Force"]
    assert utl.to_list("X-wing|Y-wing", "|") == ["X-wing", "Y-wing"]
    assert utl.to_list([506, 507], ", ") == [506, 507]

    assert utl.to_none("", NONE_VALUES) == None
    assert utl.to_none("N/A ", NONE_VALUES) == None
    assert utl.to_none(" unknown", NONE_VALUES) == None
    assert utl.to_none("Yoda", NONE_VALUES) == "Yoda"
    assert utl.to_none(("41BBY", "19BBY"), NONE_VALUES) == ("41BBY", "19BBY")

    # 3.3 CHALLENGE 03
    clone_wars_episodes = utl.read_csv_to_dicts("data-clone_wars_episodes.csv")
    print(f"clone_wars_episodes: {len(clone_wars_episodes)}")

    viewer_data = 0
    for episode in clone_wars_episodes:
        if has_viewer_data(episode):
            viewer_data += 1
    print(f"3.3 viewer_data: {viewer_data}")

    # 3.4 CHALLENGE 04
    clone_wars_episodes = convert_episode_values(clone_wars_episodes, NONE_VALUES)
    utl.write_json("stu-clone_wars-episodes_converted.json", clone_wars_episodes)

    # 3.5 CHALLENGE 05
    most_viewed_episode = get_most_viewed_episode(clone_wars_episodes)
    print(f"3.5 most_viewed_episode: {most_viewed_episode}")

    # 3.6 CHALLENGE 06

    director_episode_counts = count_episodes_by_director(clone_wars_episodes)

    # TODO Uncomment
    # Sort by count (descending), last name (ascending)
    director_episode_counts = {
        director: count
        for director, count in sorted(
            director_episode_counts.items(), key=lambda x: (-x[1], x[0].split()[-1])
        )
    }

    utl.write_json("stu-clone_wars-director_episode_counts.json", director_episode_counts)

    # 3.7 CHALLENGE 07

    articles = utl.read_json("./data-nyt_star_wars_articles.json")
    news_desks = get_news_desks(articles, NONE_VALUES)
    utl.write_json("stu-nyt_news_desks.json", news_desks)

    # 3.8 CHALLENGE 08

    news_desk_articles = group_articles_by_news_desk(news_desks, articles)
    utl.write_json("stu-nyt_news_desk_articles.json", news_desk_articles)

    # 3.9 CHALLENGE 09

    ignore = ("Business Day", "Movies")

    mean_word_counts = {}
    for news_desk, articles in news_desk_articles.items():
        if news_desk not in ignore:
            mean_word_counts[news_desk] = calculate_articles_mean_word_count(articles)

    utl.write_json("stu-nyt_news_desk_mean_word_counts.json", mean_word_counts)

    # 3.10 CHALLENGE 10

    wookiee_planets = utl.read_csv_to_dicts("data-wookieepedia_planets.csv")
    wookiee_dagobah = utl.get_nested_dict(wookiee_planets, "name", "Dagobah")
    utl.write_json("stu-wookiee_dagobah.json", wookiee_dagobah)
    wookiee_haruun_kal = utl.get_nested_dict(wookiee_planets, "system", "Al'Har system")
    utl.write_json("stu-wookiee_haruun_kal.json", wookiee_haruun_kal)

    # 3.11 CHALLENGE 11

    assert utl.to_gravity_value("1 standard") == 1.0
    assert utl.to_gravity_value("5STANDARD") == 5.0
    assert utl.to_gravity_value("0.98") == 0.98
    assert utl.to_gravity_value("N/A") == "N/A"

    assert utl.to_year_era("1032BBY") == {"year": 1032, "era": "BBY"}
    assert utl.to_year_era("19BBY") == {"year": 19, "era": "BBY"}
    assert utl.to_year_era("0ABY") == {"year": 0, "era": "ABY"}
    assert utl.to_year_era("Chewbacca") == "Chewbacca"

    # 3.12 CHALLENGE 12

    keys_path = Path("data-key_mappings.json").absolute()
    keys = utl.read_json(keys_path)
    swapi_tatooine = get_swapi_resource(SWAPI_PLANETS, {"search": "tatooine"})["results"][0]
    wookiee_tatooine = utl.get_nested_dict(wookiee_planets, "name", swapi_tatooine["name"])
    swapi_tatooine.update(wookiee_tatooine)
    tatooine = transform_planet(swapi_tatooine, keys, NONE_VALUES)
    utl.write_json("stu-tatooine.json", tatooine)

    # 3.13 CHALLENGE 13

    swapi_r2_d2 = get_swapi_resource(SWAPI_PEOPLE, {"search": "R2-D2"})["results"][0]
    wookiee_droids = utl.read_json("data-wookieepedia_droids.json")
    wookiee_r2_d2 = utl.get_nested_dict(wookiee_droids, "name", swapi_r2_d2["name"])
    swapi_r2_d2.update(wookiee_r2_d2)
    r2_d2 = transform_droid(swapi_r2_d2, keys, NONE_VALUES)
    utl.write_json("stu-r2_d2.json", r2_d2)

    # 3.14 CHALLENGE 14

    swapi_human_species = get_swapi_resource(SWAPI_SPECIES, {"search": "human"})["results"][0]
    human_species = transform_species(swapi_human_species, keys, NONE_VALUES)
    utl.write_json("stu-human_species.json", human_species)

    # 3.15 CHALLENGE 15

    swapi_anakin = get_swapi_resource(SWAPI_PEOPLE, {"search": "Anakin"})["results"][0]
    wookiee_people = utl.read_json("data-wookieepedia_people.json")
    wookiee_anakin = utl.get_nested_dict(wookiee_people, "name", swapi_anakin["name"])
    swapi_anakin.update(wookiee_anakin)
    anakin = transform_person(swapi_anakin, keys, NONE_VALUES, wookiee_planets)
    utl.write_json("stu-anakin_skywalker.json", anakin)

    swapi_obiwan = get_swapi_resource(SWAPI_PEOPLE, {"search": "Obi-Wan"})["results"][0]
    wookiee_obiwan = utl.get_nested_dict(wookiee_people, "name", swapi_obiwan["name"])
    swapi_obiwan.update(wookiee_obiwan)
    obi_wan = transform_person(swapi_obiwan, keys, NONE_VALUES, wookiee_planets)
    utl.write_json("stu-obi_wan_kenobi.json", obi_wan)

    # 3.16 CHALLENGE 16

    wookiee_starships = utl.read_csv_to_dicts("data-wookieepedia_starships.csv")
    wookiee_twilight = utl.get_nested_dict(wookiee_starships, "name", "Twilight")
    twilight = transform_starship(wookiee_twilight, keys, NONE_VALUES)
    utl.write_json("stu-twilight.json", twilight)

    # 3.17 CHALLENGE 17

    swapi_padme = get_swapi_resource(SWAPI_PEOPLE, {"search": "Padmé"})["results"][0]
    wookiee_padme = utl.get_nested_dict(wookiee_people, "name", swapi_padme["name"])
    swapi_padme.update(wookiee_padme)
    padme = transform_person(swapi_padme, keys, NONE_VALUES, wookiee_planets)
    utl.write_json("stu-padme_amidala.json", padme)

    swapi_c_3po = get_swapi_resource(SWAPI_PEOPLE, {"search": "C-3PO"})["results"][0]
    wookie_droids = utl.read_json("data-wookieepedia_droids.json")
    wookiee_c_3po = utl.get_nested_dict(wookie_droids, "name", swapi_c_3po["name"])
    swapi_c_3po.update(wookiee_c_3po)
    c_3po = transform_droid(swapi_c_3po, keys, NONE_VALUES)
    utl.write_json("stu-c_3po.json", c_3po)

    filepath = Path("data-jedi.json").absolute()
    jedi = utl.read_json(filepath)
    mace_windu, plo_koon, shaak_ti, yoda = jedi
    passenger_manifest = [padme, c_3po, r2_d2, mace_windu, plo_koon, shaak_ti, yoda]

    assert board_passengers(1, passenger_manifest) == [padme]
    assert board_passengers(4, passenger_manifest) == [padme, c_3po, r2_d2, mace_windu]

    twilight["passengers_on_board"] = board_passengers(
        twilight["max_passengers"], passenger_manifest[:3]
    )

    # 3.18 CHALLENGE 18

    assert assign_crew_members(1, ("pilot",), (anakin, obi_wan, mace_windu)) == {"pilot": anakin}
    assert assign_crew_members(
        3, ("pilot", "copilot", "navigator"), (anakin, obi_wan, mace_windu)
    ) == {"pilot": anakin, "copilot": obi_wan, "navigator": mace_windu}

    twilight["crew_members"] = assign_crew_members(
        twilight["crew_size"], ("pilot", "copilot"), (anakin, obi_wan)
    )

    r2_d2["instructions"] = ["Power up the engines"]

    # 3.19 CHALLENGE 19

    planets = [transform_planet(planet, keys, NONE_VALUES) for planet in wookiee_planets]
    planets.sort(key=lambda planet: planet["name"], reverse=True)
    utl.write_json("stu-planets_sorted_name.json", planets)

    naboo = utl.get_nested_dict(planets, "diameter_km", 12120)
    r2_d2["instructions"].append(f"Plot course for Naboo, {naboo['region']}, {naboo['sector']}")
    print(f"3.19 r2_d2 instructions: {r2_d2['instructions']}")

    planets_diameter_km = sorted(planets, key=lambda planet: (-planet["diameter_km"] if planet["diameter_km"] else 0, planet["name"]))
    utl.write_json("stu-planets_sorted_diameter.json", planets_diameter_km)
    # 3.20 CHALLENGE 20

    r2_d2["instructions"].append("Release the docking clamp")
    utl.write_json("stu-twilight_departs.json", twilight)


if __name__ == "__main__":
    main()
