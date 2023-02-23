import os
from datetime import datetime
from datetime import timedelta

from lxml import etree
from lxml.etree import _Element

NAMESPACE = {'x': 'http://www.topografix.com/GPX/1/1'}
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
INPUT_DIR = 'input'


def get_start_date(xml: _Element, last_latitude: str) -> datetime:
    data = xml.xpath(f"//x:trkpt[@lat={last_latitude}]/x:time/text()", namespaces=NAMESPACE)
    return datetime.strptime(data[1], DATE_FORMAT)


def get_end_date(xml: _Element) -> datetime:
    data = xml.xpath("//x:trkpt/x:time/text()", namespaces=NAMESPACE)
    return datetime.strptime(data[-1], DATE_FORMAT)


def get_last_latitude(xml: _Element) -> str:
    data = xml.xpath("//x:trkpt/@lat", namespaces=NAMESPACE)
    return data[-1]


def fix_date_of_valid_points(xml: _Element, start_date: datetime) -> None:
    data = xml.xpath(f"//x:trkpt/x:time", namespaces=NAMESPACE)
    new_date = start_date
    for element in data:
        element.text = new_date.strftime(DATE_FORMAT)
        new_date = new_date + timedelta(seconds=1)


def fix_elevation_for_valid_points(xml: _Element, last_latitude: str) -> None:
    elevation_elements = xml.xpath(f"//x:trkpt[@lat={last_latitude}]/x:ele/text()", namespaces=NAMESPACE)
    data = xml.xpath(f"//x:trkpt/x:ele", namespaces=NAMESPACE)
    i = 0
    count = 0
    iteration = 1
    limit = len(elevation_elements)
    for element in data:
        if count == 4:
            iteration += 1
            count = -1
        if iteration < limit:
            value = elevation_elements[iteration]
            element.text = value
            count += 1
        i += 1


def remove_invalid_points(xml: _Element, last_latitude: str, end_date: datetime) -> None:
    elements_to_delete = xml.xpath(f"//x:trkpt[@lat={last_latitude}]", namespaces=NAMESPACE)
    for element in elements_to_delete:
        element.getparent().remove(element)

    # Delete remaining point with date > last valid date
    elements_to_delete = xml.xpath("//x:trkpt/x:time", namespaces=NAMESPACE)
    for element in elements_to_delete:
        if datetime.strptime(element.text, DATE_FORMAT) > end_date:
            element.getparent().getparent().remove(element.getparent())


def set_start_datetime(xml: _Element, start_date: datetime) -> None:
    data = xml.xpath("//x:metadata/x:time", namespaces=NAMESPACE)
    data[0].text = start_date.strftime(DATE_FORMAT)


def add_activity_name(xml: _Element, name: str) -> None:
    trk_element = xml.xpath("//x:trk", namespaces=NAMESPACE)
    name_element = etree.Element("name")
    name_element.text = name
    trk_element[0].append(name_element)


def fix_activity_type(xml: _Element) -> None:
    type_element = xml.xpath("//x:trk/x:type", namespaces=NAMESPACE)
    type_value = type_element[0].text.lower()
    if any(elt in type_value for elt in ['marche', 'walk']):
        type_element[0].text = "10"
    elif any(elt in type_value for elt in ['course', 'run']):
        type_element[0].text = "9"


def clean_file() -> None:
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".gpx"):
            xml = etree.parse(f'{INPUT_DIR}/{filename}')

            last_latitude = get_last_latitude(xml)
            start_date = get_start_date(xml, last_latitude)
            end_date = get_end_date(xml)

            fix_date_of_valid_points(xml, start_date)
            fix_elevation_for_valid_points(xml, last_latitude)
            remove_invalid_points(xml, last_latitude, end_date)
            set_start_datetime(xml, start_date)
            # add_activity_name(xml, 'Name')
            fix_activity_type(xml)

            xml.write(f'output/{filename}', pretty_print=True)
        else:
            print(f'Format of {filename} not managed')


if __name__ == "__main__":
    clean_file()
