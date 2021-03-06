import feedparser
import html
from datetime import datetime
from park_api.geodata import GeoData
from park_api.util import utc_now

geodata = GeoData(__file__)


def parse_html(xml_data):
    feed = feedparser.parse(xml_data)

    try:
        last_updated = feed["entries"][0]["updated"]
        last_updated = datetime.strptime(last_updated[5:25], "%d %b %Y %H:%M:%S").isoformat()
    except KeyError:
        last_updated = utc_now()



    data = {
        "lots": [],
        "last_updated": last_updated
    }

    for entry in feed["entries"]:
        summary = parse_summary(entry["summary"])
        title_elements = parse_title(entry["title"])

        lot_identifier = html.unescape((title_elements[2] + " " + title_elements[0]).strip())
        lot = geodata.lot(lot_identifier)

        data["lots"].append({
            "name": html.unescape(title_elements[0]),
            "address": lot.address,
            "id": html.unescape(lot.id),
            "state": "open",
            "free": summary[1],
            "total": lot.total,
            "coords": lot.coords,
            "forecast": False,
            "lot_type": title_elements[2]
        })
    return data


def parse_summary(summary):
    """Parse a string from the format 'Anzahl freie Parkpl&auml;tze: 179' into both its params"""
    summary = summary.split(":")

    summary[0] = summary[0].strip()
    if "?" in summary[0]:
        summary[0] = "nodata"

    try:
        summary[1] = int(summary[1])
    except ValueError:
        summary[1] = 0
    return summary


def parse_title(title):
    """
    Parse a string from the format 'Parkhaus Bad. Bahnhof'
    """
    types = ["Parkhaus", "Parkplatz"]

    name = title
    address = ''
    type = ""
    if name.split(" ")[0] in types:
        type = name.split(" ")[0]
        name = " ".join(name.split(" ")[1:])

    return name, address, type
