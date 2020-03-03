from collections import namedtuple, defaultdict
from enum import Enum
from operator import eq, ge, gt

from exceptions import UnsupportedFeature
from models import NearEarthObject, OrbitPath


class DateSearch(Enum):
    """
    Enum representing supported date search on Near Earth Objects.
    """
    between = 'between'
    equals = 'equals'

    @staticmethod
    def list():
        """
        :return: list of string representations of DateSearchType enums
        """
        return list(map(lambda output: output.value, DateSearch))


class Query(object):
    """
    Object representing the desired search query operation to build. The Query uses the Selectors
    to structure the query information into a format the NEOSearcher can use for date search.
    """

    Selectors = namedtuple(
        'Selectors', ['date_search', 'number', 'filters', 'return_object'])
    DateSearch = namedtuple('DateSearch', ['type', 'values'])
    ReturnObjects = {'NEO': NearEarthObject, 'Path': OrbitPath}

    def __init__(self, **kwargs):
        """
        :param kwargs: dict of search query parameters to determine which SearchOperation query to use
        """
        # TODO: What instance variables will be useful for storing on the Query object?
        self.date = kwargs.get('date', None)
        self.end_date = kwargs.get('end_date', None)
        self.start_date = kwargs.get('start_date', None)
        self.filter = kwargs.get('filter', None)
        self.number = kwargs.get('number', None)
        self.return_object = kwargs.get('return_object', None)

    def build_query(self):
        """
        Transforms the provided query options, set upon initialization, into a set of Selectors that the NEOSearcher
        can use to perform the appropriate search functionality

        :return: QueryBuild.Selectors namedtuple that translates the dict of query options into a SearchOperation
        """

        # TODO: Translate the query parameters into a QueryBuild.Selectors object
        date_search = Query.DateSearch(DateSearch.equals.name, self.date) if self.date else Query.DateSearch(
            DateSearch.between.name, [self.start_date, self.end_date])

        return_object = Query.ReturnObjects.get(self.return_object)

        filters = []
        if self.filter:
            filter_options = Filter.create_filter_options(self.filter)
            for k, v in filter_options.items():
                for a_filter in v:
                    option = a_filter.split(':')[0]
                    operation = a_filter.split(':')[1]
                    value = a_filter.split(':')[-1]
                    filters.append(Filter(option, k, operation, value))

        return Query.Selectors(date_search, self.number, filters, return_object)


class Filter(object):
    """
    Object representing optional filter options to be used in the date search for Near Earth Objects.
    Each filter is one of Filter.Operators provided with a field to filter on a value.
    """
    Options = {
        # TODO: Create a dict of filter name to the NearEarthObject or OrbitalPath property
        'is_hazardous': 'is_potentially_hazardous_asteroid',
        'diameter': 'diameter_min_km',
        'distance': 'miss_distance_kilometers'
    }

    Operators = {
        # TODO: Create a dict of operator symbol to an Operators method, see README Task 3 for hint
        '=': eq,
        '>': gt,
        '>=': ge
    }

    def __init__(self, field, object, operation, value):
        """
        :param field:  str representing field to filter on
        :param field:  str representing object to filter on
        :param operation: str representing filter operation to perform
        :param value: str representing value to filter for
        """
        self.field = field
        self.object = object
        self.operation = operation
        self.value = value

    @staticmethod
    def create_filter_options(filter_options):
        """
        Class function that transforms filter options raw input into filters

        :param input: list in format ["filter_option:operation:value_of_option", ...]
        :return: defaultdict with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        """

        # TODO: return a defaultdict of filters with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        return_value = defaultdict(list)

        for filter_option in filter_options:
            a_filter = filter_option.split(':')[0]
            if hasattr(NearEarthObject(), Filter.Options.get(a_filter)):
                return_value['NearEarthObject'].append(filter_option)
            elif hasattr(OrbitPath(), Filter.Options.get(a_filter)):
                return_value['OrbitPath'].append(filter_option)

        return return_value

    def apply(self, results):
        """
        Function that applies the filter operation onto a set of results

        :param results: List of Near Earth Object results
        :return: filtered list of Near Earth Object results
        """
        # TODO: Takes a list of NearEarthObjects and applies the value of its filter operation to the
        filtered_list = []
        for neo in results:
            operation = Filter.Operators.get(self.operation)
            field = Filter.Options.get(self.field)
            val = getattr(neo, field)
            try:
                if operation(val, self.value):
                    filtered_list.append(neo)
            except Exception:
                if operation(str(val), str(self.value)):
                    filtered_list.append(neo)

        return filtered_list


class NEOSearcher(object):
    """
    Object with date search functionality on Near Earth Objects exposed by a generic
    search interface get_objects, which, based on the query specifications, determines
    how to perform the search.
    """

    def __init__(self, db):
        """
        :param db: NEODatabase holding the NearEarthObject instances and their OrbitPath instances
        """
        self.db = db
        # TODO: What kind of an instance variable can we use to connect DateSearch to how we do search?
        self.date_search_type = None
        self.date_neo = db.get_neo_date()
        self.neo_name= db.get_neo_name()

    def get_objects(self, query):
        """
        Generic search interface that, depending on the details in the QueryBuilder (query) calls the
        appropriate instance search function, then applys any filters, with distance as the last filter.

        Once any filters provided are applied, return the number of requested objects in the query.return_object
        specified.

        :param query: Query.Selectors object with query information
        :return: Dataset of NearEarthObjects or OrbitalPaths
        """
        # TODO: This is a generic method that will need to understand, using DateSearch, how to implement search
        # TODO: Write instance methods that get_objects can use to implement the two types of DateSearch your project
        # TODO: needs to support that then your filters can be applied to. Remember to return the number specified in
        # TODO: the Query.Selectors as well as in the return_type from Query.Selectors
        self.date_search_type = query.date_search.type
        date = query.date_search.values
        list_of_neo = []
        if self.date_search_type == DateSearch.equals.name:
            list_of_neo = self.apply_dateseaerch_equal(
                self.date_neo, date)
        elif self.date_search_type == DateSearch.between.name:
            list_of_neo = self.apply_datesearch_between(
                self.date_neo, date[0], date[1])
        orbit = self.return_orbit_paths_from_neos(list_of_neo)

        distance_filter = None
        for a_filter in query.filters:
            if a_filter.field == 'distance':
                distance_filter = a_filter
                continue
            list_of_neo = a_filter.apply(list_of_neo)
        orbit = self.return_orbit_paths_from_neos(list_of_neo)

        filtered_orbit = orbit
        filtered_neos = list_of_neo

        if distance_filter:
            filtered_orbit = distance_filter.apply(orbit)

            filtered_neos = self.return_neo_from_orbit_path(filtered_orbit)

        filtered_neos = list(set(filtered_neos))
        filtered_orbit = list(set(filtered_orbit))

        if query.return_object == OrbitPath:
            return filtered_orbit[: int(query.number)]
        return filtered_neos[: int(query.number)]

    def apply_dateseaerch_equal(self, a_neo_map, date):
        """ This function perfoms the date filtering when only one date and return the results

        :param a_neo_map: dict of date to neos mappings
                date: string date to filter for
        :return: A list of filtered neos
        """
        result = []
        for key, value in a_neo_map.items():
            if key == date:
                result += value
        return result

    def apply_datesearch_between(self, a_neo_map, start_date, end_date):
        """ This functions performs the date filtering when more than one date is specified and returns the result

        :param a_neo_map: dict of date to neos mappings
                start_date: string start date for filtering
                end_date: string end date for filtering
        :return: A list of filtered neos"""
        result = []
        for key, value in a_neo_map.items():
            if key >= start_date and key <= end_date:
                result += value
        return result

    def return_neo_from_orbit_path(self, orbit_paths):
        result = [self.neo_name.get(
            path.neo_name) for path in orbit_paths]
        return result

    def return_orbit_paths_from_neos(self, neos):
        return_val = []

        for neo in neos:
            return_val += neo.orbits

        return return_val
