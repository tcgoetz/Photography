#!/usr/bin/env python3

"""A script that formats exif metadata from an image for adding to a image posting."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import sys
import argparse
from fractions import Fraction
import datetime
import exiftool


#
# Maps camera names in EXIF to more friendly names. If the camera name in EXIF is not found here, the value from EXIF will be used.
#
camera_map = {
    "Canon EOS 5D": "Canon 5D",
    "Canon EOS 5D Mark II": "Canon 5Dm2",
    "Canon EOS 7D": "Canon 7D",
    "Canon EOS 10D": "Canon 10D",
    "Canon EOS 30D": "Canon 30D",
    "Canon PowerShot G7 X": "Canon G7X",
    "Canon PowerShot G9": "Canon G9",
    "Canon PowerShot G12": "Canon G12",
    "Canon PowerShot G15": "Canon G15",
    "DC-LX100M2": "Panosonic LX100M2",
    'ILCE-6000': 'Sony a6000',
    'ILCE-6500': 'Sony a6500',
    'X-E3': 'Fuji X-E3',
    'X-T3': 'Fuji X-T3',
    'X-T4': 'Fuji X-T4',
    'X-T30': 'Fuji X-T30',
    'X-H2': 'Fuji X-H2'
}

camera_hash_map = {
    "fujifilm": "#FujiFilm #FujiXSeries #FujiPhotography",
    "sony": "#SonyAlpha"
}


#
# Maps lens names in EXIF to more friendly names. If the lens name in EXIF is not found here, the value from EXIF will be used.
#
lens_map = {
    # Canon 50 1.4
    '50.0mm': 'Canon 50mm F1.4',
    'EF50mm/1.4 USM': 'Canon 50mm F1.4',
    'EF50mm f/1.4 USM': 'Canon 50mm F1.4',
    'Canon EF 50mm f/1.4 USM': 'Canon 50mm F1.4',
    # Canon 85 1.8
    '85.0mm': 'Canon 85mm F1.8',
    'EF85/1.8 USM': 'Canon 85mm F1.8',
    'EF85 f/1.8 USM': 'Canon 85mm F1.8',
    'Canon EF 85mm f/1.8 USM': 'Canon 85mm F1.8',
    'Canon EF 100mm f/2.8 L Macro IS USM': 'Canon 100mm F2.8 Macro',
    # Canon 180 macro
    '180.0mm': 'Canon 180mm F3.5 Macro',
    'EF180mm f/3.5 L Macro USM': 'Canon 180mm F3.5 Macro',
    'Canon EF 180mm f/3.5 L USM': 'Canon 180mm F3.5 Macro',
    'EF180mm f/3.5 L Macro USM +1.4x': 'Canon 180mm F3.5 Macro with 1.4x TC',
    'EF180mm f/3.5 L Macro USM +2.0x': 'Canon 180mm F3.5 Macro with 2.0x TC',
    # Canon 300 2.8
    '300.0mm': 'Canon 300mm F2.8',
    'EF300mm f/2.8L IS USM': 'Canon 300mm F2.8',
    'EF300mm f/2.8L IS USM +1.4x': 'Canon 300mm F2.8 with 1.4x TC',
    'EF300mm f/2.8L IS USM +2.0x': 'Canon 300mm F2.8 with 2.0x TC',
    # Canon 300 f4
    'EF300mm f/4L USM': 'Canon 300mm F4',
    'EF300mm f/4L USM +1.4x': 'Canon 300mm F4 with 1.4x TC',
    '17.0-40.0mm': 'Canon 17-40mm F4',
    'EF17-40mm f/4L USM': 'Canon 17-40mm F4',
    'EF24-105mm f/4L IS USM': 'Canon 24-105mm F4',
    '20.0-35.0mm': 'Canon 20-35mm F3.5-4.5',
    '70.0-200.0mm': 'Canon 70-200mm F4',
    'EF70.0-200.0mm f/4L USM': 'Canon 70-200mm F4',
    # Sony
    'EF 50mm F1.8': 'Sony 50mm F1.8',
    'EF 70-200mm F4 G OSS': 'Sony 70-200mm F4',
    'FE 90mm F2.8 Macro G OSS': 'Sony 90mm F2.8 Macro',
    'E PZ 16-50mm F3.5-5.6 OSS': 'Sony 16-50mm F3.5-5.6',
    'E 10-18mm F4 OSS': 'Sony 10-18mm F4',
    'E 16-70mm F4 ZA OSS': 'Sony 16-70mm F4',
    '16mm F1.4 DC DN | Contemporary 016': 'Sigma 16mm F1.4',
    '16mm F1.4 DC DN | Contemporary 017': 'Sigma 16mm F1.4',
    # Fuji
    "XF16mmF1.4 R WR": "Fuji 16mm F1.4",
    "XF35mmF1.4 R": "Fuji 35mm F1.4",
    "XF10-24mmF4 R OIS": "Fuji 10-24mm F4",
    "XF16-55mmF2.8 R LM WR": "Fuji 16-55mm F2.8",
    "XF18-55mmF2.8-4 R LM OIS": "Fuji 18-55mm F2.8-4",
    "XF55-200mmF3.5-4.8 R LM OIS": "Fuji 55-200mm F3.5-4.8",
    # Adapted Lenses
    "Metabones 180/3.5": "Canon 180mm F3.5 Macro on a Metabones adapter"
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
    "panoramic": "#Panoramic",
    "portrait": "#PortraitPhotography",
    "reflection": "#Reflection",
    "sailboat": "#Sailboat",
    "saltmarsh": "#Saltmarsh",
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
    "ocean": (IsDay(2), "#OceanWednesday"),
    "waterfall": (IsDay(2), "#WaterfallWednesday"),
    "waves": (IsDay(2), "#WavyWednesday"),
    "tree": (IsDay(2), "#ThickTrunkThursday"),
    "flower": (IsDay(4), "#FlowerFriday"),
    "trail": (IsDay(4), "#FootPathFriday"),
    "window": (IsDay(4), "#FensterFreitag #WindowFriday"),
    "cat": (IsDay(5), "#Caturday"),
    "fog": (IsDay(6), "#SilentSunday"),
    "moody": (IsDay(6), "#SilentSunday")
}


#
# Adds hashtags for popular locations.
#
location_map = {
    "Acadia National Park": "#AcadiaNationalPark",
    "Ashland State Park": "#AshlandStatePark",
    "Beaufort": "#OBX #OuterBanks",
    "Crawford Notch State Park": "#CrawfordNotchStatePark",
    "Franconia Notch State Park": "#FranconiaNotchStatePark",
    "Wareham": "#BuzzardsBay",
    "Westport": "#BuzzardsBay",
    "White Mountain National Forest": "#WhiteMountainNationalForest",
    "Whitehall State Park": "#WhitehallStatePark",
    "Yellowstone National Park": "#YellowstoneNationalPark",
    "Zion National Park": "#ZionNationalPark"
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
        'MI': '#michigan',
        'MN': '#minnesota',
        'MO': '#missouri',
        'MP': '#NorthernMarianaIslands',
        'MS': '#mississippi',
        'MT': '#montana',
        'NA': '#national',
        'NC': '#NorthCarolina',
        'North Carolina': '#NorthCarolina',
        'ND': '#NorthDakota',
        'NE': '#Nebraska',
        'NH': '#NewHampshire',
        'NJ': '#NewJersey',
        'NM': '#NewMexico',
        'NV': '#nevada',
        'NY': '#NewYork',
        'OH': '#ohio',
        'OK': '#oklahoma',
        'OR': '#Oregon',
        "Oregon": "#Oregon",
        'PA': '#pennsylvania',
        'PR': '#PuertoRico',
        'RI': '#RhodeIsland',
        'SC': '#SouthCarolina',
        'SD': '#SouthdDkota',
        'TN': '#tennessee',
        'TX': '#texas',
        'UT': '#utah',
        'VA': '#virginia',
        'VI': '#VirginsIslands',
        'VT': '#vermont',
        'WA': '#washington',
        'WI': '#wisconsin',
        'WV': '#WestVirginia',
        'WY': '#wyoming'
}


country_code_map = {
    "AT": "#Austria"
}

day_of_the_week = {
    0: "#PhotoMonday"
}


base_hash_tags = '#Photography #AmateurPhotography #MyPhoto'


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

    title = metadata.get_iptc('ObjectName')
    caption = metadata.get_iptc('Caption-Abstract')
    if caption:
        title = f"{title} - {caption}"

    sublocation = metadata.get_iptc('Sub-location')
    city = metadata.get_iptc('City')
    state = metadata.get_iptc('Province-State')
    country = metadata.get_iptc('Country-PrimaryLocationName')
    country_code = metadata.get_iptc('Country-PrimaryLocationCode')
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

    if args.gps:
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

    if args.critique:
        hash_tags += " #photocritique"
        posting_notes = f'{title}\n{location}\n\n{gps}{photo_data}\n\nCritiques welcome. Thanks for taking the time to look at my photo.\n\n{end_text}'
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