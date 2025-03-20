#!/usr/bin/env python3

"""A script that formats exif metadata from an image for adding to a image posting."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import sys
import os
import argparse
from fractions import Fraction
import datetime
import exiftool
import json


camera_hash_map = {
    "canon": "#CanonPhotography",
    "fujifilm": "#FujiFilm #FujiXSeries #FujiPhotography",
    "sony": "#SonyAlpha"
}


#
# Reformats and filters out keywords we don't want to publish. Keyword in IPTC that are not present here, will be ignored.
#
keywords_map = {
    "adapted lens": "#AdaptedLens",
    "beach": "#BeachPhotography",
    "bird": "#bird #BirdPhotography",
    "blackandwhite": "#BlackAndWhitePhotography",
    "canoe": "#paddling",
    "capecod": "#CapeCod",
    "cat": "#cat #CatsOfPixelfed",
    "closeup": "#CloseupPhotography",
    "clouds": "#Clouds",
    "fall": "#Fall",
    "fog": "#Fog",
    "foliage": "#Foliage",
    "flower": "#Flower #BloomScrolling",
    "garden": "#Garden",
    "golden hour": "#GoldenHour",
    "hand held": "#HandHeld",
    "hdr": "#hdr",
    "hiking": "#Hiking",
    "historic": "#Historic",
    "kayak": "#Paddling",
    "lake": "#Lake",
    "landscape": "#LandscapePhotography",
    "lighthouse": "#Lighthouse",
    "macro": "#MacroPhotography",
    "mountain": "#Mountains",
    "mountains": "#Mountains",
    "nationalforest": "#NationalForest",
    "nationalpark": "#NationalPark",
    "night": "#NightPhotography",
    "ocean": "#Ocean",
    "panoramic": "#Panorama",
    "portrait": "#PortraitPhotography",
    "reflection": "#Reflection",
    "sailboat": "#Sailboat",
    "saltmarsh": "#Saltmarsh",
    "scenic": "#ScenicPhotography",
    "seascape": "#SeascapePhotography",
    "shorebird": "#ShoreBird",
    "sky": "#Sky",
    "spring": "#Spring",
    "statepark": "#StatePark",
    "summer": "#Summer",
    "sunrise": "#Sunrise",
    "sunset": "#Sunset",
    "waterfall": "#Waterfall",
    "waves": "#Waves",
    "weather": "#Weather",
    "wildlife": "#WildLifePhotography",
    "winter": "#Winter",
    "wmnf": "#WhiteMountainNationalForest"
}


def IsDay(day_of_the_week):
    return (datetime.datetime.today().weekday() == day_of_the_week)


keyword_conditional_map = {
    "dog": (IsDay(0), "#MonDog"),
    "blackandwhite": (IsDay(0), "#MonochromeMonday"),
    "mountain": (IsDay(0), "#MountainMonday"),
    "mountains": (IsDay(0), "#MountainMonday"),
    "tree": (IsDay(1), "#ThickTrunkThursday"),
    "ocean": (IsDay(2), "#OceanWednesday"),
    "waterfall": (IsDay(2), "#WaterfallWednesday"),
    "waves": (IsDay(2), "#WavyWednesday"),
    "flower": (IsDay(4), "#FlowerFriday"),
    "fungus": (IsDay(4), "#FungiFriday"),
    "mushroom": (IsDay(4), "#FungiFriday"),
    "trail": (IsDay(4), "#FootPathFriday"),
    "window": (IsDay(4), "#FensterFreitag #WindowFriday"),
    "cat": (IsDay(5), "#Caturday"),
    "fog": (IsDay(6), "#SilentSunday"),
    "moody": (IsDay(6), "#SilentSunday")
}


#
# Adds hashtags for US states.
#
state_map = {
        'AK': '#alaska',
        'AL': '#alabama',
        'AR': '#arkansas',
        'AS': '#AmericanSamoa',
        'AZ': '#arizona',
        'CA': '#California',
        'California': '#California',
        'CO': '#colorado',
        'CT': '#connecticut',
        'DC': '#DistrictOfColumbia',
        'DE': '#delaware',
        'FL': '#florida',
        'GA': '#georgia',
        'GU': '#guam',
        'HI': '#hawaii',
        'IA': '#iowa',
        'ID': '#idaho',
        'IL': '#illinois',
        'IN': '#indiana',
        'KS': '#kansas',
        'KY': '#kentucky',
        'LA': '#louisiana',
        'MA': '#Massachusetts',
        'Massachusetts': '#Massachusetts',
        'MD': '#maryland',
        'ME': '#Maine',
        'Maine': '#Maine',
        'MI': '#Michigan',
        'MN': '#Minnesota',
        'MO': '#Missouri',
        'MP': '#NorthernMarianaIslands',
        'MS': '#Mississippi',
        'MT': '#Montana',
        'NA': '#national',
        'NC': '#NorthCarolina',
        'North Carolina': '#NorthCarolina',
        'ND': '#NorthDakota',
        'NE': '#Nebraska',
        'NH': '#NewHampshire',
        'New Hampshire': '#NewHampshire',
        'NJ': '#NewJersey',
        'NM': '#NewMexico',
        'NV': '#Nevada',
        'NY': '#NewYork',
        'OH': '#Ohio',
        'OK': '#Oklahoma',
        'OR': '#Oregon',
        "Oregon": "#Oregon",
        'PA': '#Pennsylvania',
        'PR': '#PuertoRico',
        'RI': '#RhodeIsland',
        'SC': '#SouthCarolina',
        'SD': '#SouthdDkota',
        'TN': '#Tennessee',
        'TX': '#Texas',
        'UT': '#Utah',
        'VA': '#Virginia',
        'VI': '#VirginsIslands',
        'VT': '#Vermont',
        'WA': '#Washington',
        'WI': '#Wisconsin',
        'WV': '#WestVirginia',
        'WY': '#Wyoming'
}


country_code_map = {
    "AT": "#Austria",
    "CA": "#Canada",
    "IE": "#Ireland"
}

day_of_the_week = {
    0: "#PhotoMonday"
}


def gps_degrees_mins_secs_to_decimal(decimal, direction):
    if direction == 'W' or direction == 'S':
        decimal *= -1
    return decimal


class MetaData:
    def __init__(self, file, **kwargs):
        with exiftool.ExifToolHelper(**kwargs) as et_helper:
            self.metadata = et_helper.get_metadata(file)[0]

    def get_all(self, type):
        return {k: v for k, v in self.metadata.items() if k.startswith(type + ":")}

    def get_exif(self, property_name):
        return self.metadata.get("EXIF:" + property_name)

    def get_iptc(self, property_name):
        return self.metadata.get("IPTC:" + property_name)

    def get_xmp(self, property_name):
        return self.metadata.get("XMP:" + property_name)


def main(argv):
    """Copy metadata."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path and name of the image file.", type=str, required=True)
    parser.add_argument("-o", "--output", help="Path and name of the output file.", type=str)
    parser.add_argument("-e", "--exiftool", help="Full path to exiftool.", type=str)
    parser.add_argument("-z", "--mapzoom", help="Zoom level for OSM map link.", type=int, default=17)
    parser.add_argument("-d", "--dump", help="Dumpp image EXIF, IPTC, and XMP data.", action="store_true", default=False)
    parser.add_argument("-g", "--gps", help="Add OSM link using gps coordinates from EXIF.", action="store_true", default=False)
    parser.add_argument("-c", "--critique", help="Request critiques.", action="store_true", default=False)
    parser.add_argument("-a", "--alttxt", help="Output ALT text from XMP.", action="store_true", default=False)
    parser.add_argument("-r", "--copyright", help="Output copyright notice based on IPTC copyright data.", action="store_true", default=False)
    parser.add_argument("-n", "--noai", help="Add text to the copyright notice to forbid use in training AIs.", action="store_true", default=False)
    parser.add_argument("-s", "--short", help="Short form.", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Echo output to the screen.", action="store_true", default=False)
    args = parser.parse_args()
    
    if args.exiftool:
        print(f"Using exiftool from {args.exiftool}")
        metadata = MetaData(args.file, executable=args.exiftool)
    else:
        metadata = MetaData(args.file)

    if args.dump:
        print(f"exif:\n{metadata.get_all('EXIF')}")
        print(f"iptc:\n{metadata.get_all('IPTC')}")
        print(f"iptc:\n{metadata.get_all('XMP')}\n")

    with open(os.path.dirname(__file__) + os.sep + 'photo_post_data.json') as json_file:
        config = json.load(json_file)

    base_hash_tags = config.get('base_hash_tags', "")
    # Maps camera names in EXIF to more friendly names. If the camera name in EXIF is not found here, the value from EXIF will be used.
    camera_map = config.get('camera_map', {})
    # Maps lens names in EXIF to more friendly names. If the lens name in EXIF is not found here, the value from EXIF will be used.
    lens_map = config.get('lens_map', {})
    # Adds hashtags for popular locations.
    location_map = config.get('location_map', {})
    # don't display location or map link for these
    private_places = config.get('private_places', {})

    title = metadata.get_iptc('ObjectName')
    caption = metadata.get_iptc('Caption-Abstract')
    if caption:
        title = f"{title} - {caption}"

    sublocation = metadata.get_iptc('Sub-location')
    city = metadata.get_iptc('City')
    state = metadata.get_iptc('Province-State')
    country = metadata.get_iptc('Country-PrimaryLocationName')
    country_code = metadata.get_iptc('Country-PrimaryLocationCode')
    private_place = sublocation in private_places
    if private_place:
        location = f"{city}, {state}, {country}"
    else:
        location = f"{sublocation}, {city}, {state}, {country}"

    when_taken = datetime.datetime.strptime(metadata.get_exif('DateTimeOriginal'), "%Y:%m:%d %H:%M:%S")
    shutter_speed = Fraction(float(metadata.get_exif('ExposureTime'))).limit_denominator()
    lens = lens_map.get(metadata.get_exif('LensModel'), metadata.get_exif('LensModel'))
    camera = camera_map.get(metadata.get_exif('Model'), metadata.get_exif('Model'))
    photo_data = f"Taken on {when_taken} with {lens} on {camera} with exposure {shutter_speed}s @ f/{metadata.get_exif('FNumber')} @ {metadata.get_exif('FocalLength')}mm @ {metadata.get_exif('ISO')} ISO"

    hash_tags = base_hash_tags
    for keyword in metadata.get_iptc('Keywords'):
        keyword_decoded = keyword.lower()
        hash_tag = keywords_map.get(keyword_decoded)
        if hash_tag:
            hash_tags += " " + hash_tag
        test, hash_tag = keyword_conditional_map.get(keyword_decoded, (None, None))
        if test:
            hash_tags += " " + hash_tag

    camera_hash_tag = camera_hash_map.get(metadata.get_exif('Make').lower())
    if camera_hash_tag:
        hash_tags += " " + camera_hash_tag

    location_hash_tag = location_map.get(sublocation) or location_map.get(city)
    if location_hash_tag:
        hash_tags += " " + location_hash_tag
    state_hash_tag = state_map.get(state)
    if state_hash_tag:
        hash_tags += " " + state_hash_tag
    country_hash_tag = country_code_map.get(country_code)
    if country_hash_tag:
        hash_tags += " " + country_hash_tag

    if args.gps and not private_place:
        lat = gps_degrees_mins_secs_to_decimal(metadata.get_exif('GPSLatitude'), metadata.get_exif('GPSLatitudeRef'))
        long = gps_degrees_mins_secs_to_decimal(metadata.get_exif('GPSLongitude'), metadata.get_exif('GPSLongitudeRef'))
        gps = f"Photo location: https://www.openstreetmap.org/#map={args.mapzoom}/{lat}/{long}\n\n"
    else:
        gps = ""

    copyright = metadata.get_iptc("CopyrightNotice")
    if args.copyright and copyright:
        copyright = f"\n{copyright}. All rights reserved."
    else:
        copyright= ""
    if args.noai:
        copyright += " Training an AI on this image is expressly forbidden."

    day_hash = day_of_the_week.get(datetime.datetime.today().weekday())
    if day_hash:
        hash_tags += " " + day_hash

    if args.short:
        end_text = f"{hash_tags}\n{copyright}"
    else:
        end_text = hash_tags

    description_txt = metadata.get_xmp("ExtDescrAccessibility")
    if description_txt:
        description = description_txt + "\n\n"
    else:
        description = ""

    if args.critique:
        hash_tags += " #PhotoCritique"
        posting_notes = f'{title}\n{location}\n\n{description}{gps}{photo_data}\n\nCritiques welcome. Thanks for taking the time to look at my photo.\n\n{end_text}'
    else:
        posting_notes = f'{title}\n{location}\n\n{gps}{photo_data}\n\n{end_text}'

    alt_txt = metadata.get_xmp("AltTextAccessibility")
    if args.alttxt and alt_txt:
        posting_notes += f"\n\n-- ALT TXT\n\n{alt_txt}{copyright}"

    if args.output:
        with open(args.output, "w") as text_file:
            text_file.write(posting_notes)
    if args.verbose:
        print(posting_notes)


if __name__ == "__main__":
    main(sys.argv[1:])