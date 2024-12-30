#!/usr/bin/env python3

"""A script that formats exif metadata from an image for adding to a image posting."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import sys
import argparse
from exif import Image
from iptcinfo3 import IPTCInfo
from fractions import Fraction
import datetime

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
    'EF17-40mm F/4L USM': 'Canon 17-40mm F4',
    'EF24-105mm f/4L IS USM': 'Canon 24-105mm F4',
    '20.0-35.0mm': 'Canon 20-35mm F3.5-4.5',
    '70.0-200.0mm': 'Canon 70-200mm F4',
    'EF70.0-200.0mm f/4L USM': 'Canon 70-200mm F4',
    # Sony
    'EF 50mm F1.8': 'Sony 50mm F1.8',
    'EF 70-200mm F4 G OSS': 'Sony 70-200mm F4',
    'EF 90mm F2.8 Macro G OSS': 'Sony 90mm F2.8 Macro',
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
}

#
# Reformats and filters out keywords we don't want to publish. Keyword in IPTC that are not present here, will be ignored.
#
keywords_map = {
    "adapted lens": "#AdaptedLens",
    "beach": "#beach",
    "bird": "#bird",
    "blackandwhite": "#BlackAndWhitePhotography",
    "canoe": "#paddling",
    "capecod": "#CapeCod",
    "cat": "#cat #CatsOfPixelfed",
    "closeup": "#CloseupPhotography",
    "clouds": "#clouds",
    "fall": "#fall",
    "fog": "#fog",
    "folliage": "#folliage",
    "flower": "#flower",
    "garden": "#garden",
    "golden hour": "#GoldenHour",
    "hdr": "#hdr",
    "hiking": "#hiking",
    "kayak": "#paddling",
    "lake": "#lake",
    "landscape": "#LandscapePhotography",
    "macro": "#MacroPhotography",
    "mountain": "#mountains",
    "mountains": "#mountains",
    "nationalforest": "#NationalForest",
    "nationalpark": "#NationalPark",
    "ocean": "#ocean",
    "panoramic": "#panoramic",
    "relection": "#reflection",
    "saltmarsh": "#saltmarsh",
    "seascape": "#SeascapePhotography",
    "shorebird": "#ShoreBird",
    "sky": "#sky",
    "statepark": "#StatePark",
    "summer": "#summer",
    "sunrise": "#sunrise",
    "sunset": "#sunset",
    "waterfall": "#waterfall",
    "weather": "#weather",
    "wildlife": "#wildlife",
    "winter": "#winter",
    "wmnf": "#wmnf"
}

#
# Adds hashtags for popular locations.
#
location_map = {
    "Acadia National Park": "#AcadiaNationalPark",
    "Ashland State Park": "#AshlandStatePark",
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
        'CA': '#california',
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
        'MD': '#maryland',
        'ME': '#maine',
        'MI': '#michigan',
        'MN': '#minnesota',
        'MO': '#missouri',
        'MP': '#NorthernMarianaIslands',
        'MS': '#mississippi',
        'MT': '#montana',
        'NA': '#national',
        'NC': '#NorthCarolina',
        'ND': '#NorthDakota',
        'NE': '#Nebraska',
        'NH': '#NewHampshire',
        'NJ': '#NewJersey',
        'NM': '#NewMexico',
        'NV': '#nevada',
        'NY': '#NewYork',
        'OH': '#ohio',
        'OK': '#oklahoma',
        'OR': '#oregon',
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


def gps_degrees_mins_secs_to_decimal(gps_tuple, direction):
    degrees, minutes, seconds = gps_tuple
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    if direction == 'W' or direction == 'S':
        decimal *= -1
    return decimal


def iptc_get(iptc, field_name):
    field = iptc[field_name]
    if field:
        return field.decode("utf-8")


def main(argv):
    """Copy metadata."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path and name of the image file.", type=str)
    parser.add_argument("-o", "--output", help="Path and name of the output file.", type=str)
    parser.add_argument("-z", "--mapzoom", help="Zoom level for OSM map link.", type=int, default=17)
    parser.add_argument("-d", "--dump", help="Dumpp image EXIF and IPTC data.", action="store_true", default=False)
    parser.add_argument("-g", "--gps", help="Add OSM link with gps.", action="store_true", default=False)
    parser.add_argument("-c", "--critique", help="Request critiques.", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Echo output to the screen.", action="store_true", default=False)
    args = parser.parse_args()

    if not args.file:
        print("--file required")
        sys.exit()

    with open(args.file, 'rb') as image_file:
        exif = Image(image_file)
        iptc = IPTCInfo(args.file)

        if not exif.has_exif:
            print(f"{args.file} has no exif data!")
            sys.exit()

    if args.dump:
        print(f"exif:\n{exif.get_all()}")
        print(f"iptc:\n{str(iptc)}")

    title = iptc['object name'].decode("utf-8")
    caption = iptc_get(iptc, 'caption/abstract')
    if caption:
        title = f"{title} - {caption}"

    sublocation = iptc_get(iptc, 'sub-location')
    city = iptc_get(iptc, 'city')
    state = iptc_get(iptc, 'province/state')
    country = iptc_get(iptc, 'country/primary location name')
    country_code = iptc_get(iptc, 'country/primary location code')
    location = f"{sublocation}, {city}, {state}, {country}"

    when_taken = datetime.datetime.strptime(exif.datetime_original, "%Y:%m:%d %H:%M:%S")
    shutter_speed = Fraction(float(exif.exposure_time)).limit_denominator()
    lens = lens_map.get(exif.lens_model, exif.lens_model)
    camera = camera_map.get(exif.model, exif.model)
    photo_data = f"Taken on {when_taken} with {lens} on {camera} with exposure {shutter_speed}s @ f/{exif.f_number} @ {exif.focal_length}mm @ {exif.photographic_sensitivity} ISO"

    hash_tags = '#photography'
    for keyword in iptc['keywords']:
        hash_tag = keywords_map.get(keyword.decode("utf-8").lower())
        if hash_tag:
            hash_tags += " " + hash_tag
    
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
        lat = gps_degrees_mins_secs_to_decimal(exif.gps_latitude, exif.gps_latitude_ref)
        long = gps_degrees_mins_secs_to_decimal(exif.gps_longitude, exif.gps_longitude_ref)
        gps = f"Photo location: https://www.openstreetmap.org/#map={args.mapzoom}/{lat}/{long}\n"
    else:
        gps = ""

    if args.critique:
        hash_tags += " #photocritique"
        posting_notes = f'{title}\n{location}\n{gps}{photo_data}\n\nCritiques welcome. Thanks for taking the time to look at my photo.\n\n{hash_tags}'
    else:
        posting_notes = f'{title}\n{location}\n\n{photo_data}\n\n{hash_tags}'

    if args.output:
        with open(args.output, "w") as text_file:
            text_file.write(posting_notes)
    if args.verbose:
        print(posting_notes)


if __name__ == "__main__":
    main(sys.argv[1:])