from xml.etree import ElementTree


def parse_flights(file_name):
    itineraries_dict = dict()
    root = ElementTree.parse(file_name).getroot()
    itineraries = root.find('PricedItineraries')
    flights = itineraries.findall('Flights')
    for flight in flights:
        onward_flights = get_flights(flight.find('OnwardPricedItinerary'))
        onward_flight_list = list()
        itineraries_key = tuple()  # unhashable key
        for flight_part in onward_flights:
            source = flight_part.find('Source').text
            destination = flight_part.find('Destination').text
            itineraries_key = itineraries_key + tuple([source, destination])  # redefine tuple to add new key points
            onward_flight_list.append(parse_flight_part_dict(flight_part))
        return_flights = get_flights(flight.find('ReturnPricedItinerary'))
        return_flight_list = list()
        for flight_part in return_flights:
            return_flight_list.append(parse_flight_part_dict(flight_part))
        itineraries_dict[itineraries_key] = (onward_flight_list, return_flight_list)
    return itineraries_dict


def get_flights(element):
    if element:
        element = element.find('Flights')
        if element:
            res = element.findall('Flight')
            return res
    return []


def parse_flight_part_dict(xml_element):
    res = {
        'FlightNumber': xml_element.find('FlightNumber').text,
        'Source': xml_element.find('Source').text,
        'Destination': xml_element.find('Destination').text,
        'DepartureTimeStamp': xml_element.find('DepartureTimeStamp').text,
        'ArrivalTimeStamp': xml_element.find('ArrivalTimeStamp').text,
        'NumberOfStops': xml_element.find('NumberOfStops').text,
    }
    return res


def get_diff(first_dict, second_dict):
    diff_list = list()
    first_set = set(first_dict)
    second_set = set(second_dict)
    intersect = first_set.intersection(second_set)
    for removed_element in first_set - intersect:
        diff_list.append('removed itinerary {}'.format(removed_element))
    for added_element in second_set - intersect:
        diff_list.append('added itinerary {}'.format(added_element))
    for changed in intersect:
        diff_list.extend(get_part_flight_diff(changed, first_dict, second_dict))  # iterate through generator
    return diff_list


def get_part_flight_diff(changed, first_dict, second_dict):
    for ind, direction in ((0, 'onward'), (1, 'return')):
        flight_first = first_dict[changed][ind]
        flight_second = second_dict[changed][ind]
        if flight_first != flight_second:
            if not flight_first:
                yield 'On itinerary {1} {0} direction added'.format(direction, changed)
                continue
            if not flight_second:
                yield 'On itinerary {1} {0} direction removed'.format(direction, changed)
                continue
            for first_part_flight_dict, second_part_flight_dict in zip(flight_first, flight_second):
                for key, val in first_part_flight_dict.items():
                    if val != second_part_flight_dict[key]:
                        yield 'On {0} direction itinerary {1}, {2} changed from {3} to {4} ({5}-{6} Flight point)'.\
                            format(direction, changed, key, val, second_part_flight_dict[key],
                                   first_part_flight_dict['Source'], first_part_flight_dict['Destination'])


if __name__ == "__main__":
    first_name = 'RS_Via-3.xml'
    second_name = 'RS_ViaOW.xml'
    first_dict = parse_flights(first_name)
    second_dict = parse_flights(second_name)
    res = get_diff(first_dict, second_dict)
    for entry in res:
        print(entry)
