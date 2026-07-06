# Photo Post Data

A script that generates text formated metadata for posting photos to photo sharing websites based on EXIF, IPTC, and XMP data in the image file. I use Lightroom and have added an export preset for photo sharing websites. It runs this script against the exported JPEG and generates a text file in the same directory as the JPEG with the photo meta data.

One of the issues I had in moving from a photo sharing website like Flickr to a website like PixelFed is that Flickr displays all of the photo metadata for you. On PixelFed, you have to put all of the metadata you want to show in the description. Transcribing all of the metadata for every photo was
a pain, so I wrote a script to do it for me. Now I just paste the oputput of the script into the description box when posting a photo.

### Dependancies

The scrip[t is written in [Python](https://www.python.org/) and you need Python installed.
You need [exiftool](https://exiftool.org/) installed on your machine. I installed in with [Homebrew](https://brew.sh/) (MacOS).

### Example invocation:

> python3 /Users/tgoetz/Projects/Photography/PhotoPostData/photo_post_data.py --critique --gps --alttxt --copyright --file /Users/tgoetz/Downloads/_DSF8315.jpg --output /Users/tgoetz/Downloads/_DSF8315.txt

### Example output:

> Crows Fly Over Mt Mansfield Summit - Lake Champlain in the distance.
> Long Trail, Stowe, Vermont, United States  
> 
> Critiques welcome. Thank you for taking the time to look at my photo.  
> 
> Date and time: 2026-06-16 12:09:41  
> Location: https://www.openstreetmap.org/?mlat=44.543708&mlon=-72.814486#map=15/44.54588/-72.80704  
> Camera: Fuji X-H2  
> Lens: Fuji 16-55mm F2.8  
> Exposure: 1/300s @ f/11  
> Focal length: 16mm  
> 35mm equivalent focal length: 24mm  
> ISO: 200  
> Flash: no  
> Tripod: no  
> 
> #Photography #AmateurPhotography #MyPhoto #PhotoOfTheDay #StatePark #Clouds #Hiking #optOutside #LandscapePhotography #Mountains #MountainMonday #Spring #Weather #FujiFilm #FujiXSeries #FujiPhotography #Vermont #PhotoMonday #FotoMontag #PhotoCritique

[Post](https://pixelfed.social/p/tcgoetz/979709470311847470) with example output.

## Integrating the Script into Lightroom

I have a export preset in Lightroom that uses Jeffrey Friedl's ["Run Any Command"](https://regex.info/blog/lightroom-goodies/run-any-command) plugin to run the script after the export. This is the template I use with "Run Any Command":

> python3 PhotoPostData/photo_post_data.py --exiftool "/opt/homebrew/bin/exiftool" --critique --alttxt --gps --copyright --noai --file {NAME}.jpg --output {NAME}.txt

## Data Mapping

| Post Field           | Source | Source Field                                                     |
| -------------------- | ------ | ---------------------------------------------------------------- |
| Post Title           | IPTC   | ObjectName and Caption-Abstract                                  |
| Post Location        | IPTC   | Sub-location, City, Province-State, Country-PrimaryLocationName  |
| Date and Time        | EXIF   | DateTimeOriginal                                                 |
| Post Map Link        | IPTC   | GPSLatitude, GPSLatitudeRef, GPSLongitude, GPSLongitudeRef       |
| Camera and Lens      | EXIF   | Model, LensModel                                                 |
| Exposure Info        | EXIF   | ExposureTime, FNumber, FocalLength, ISO, Flash                   |
| Posting Hashtags     | IPTC   | Keywords, Country-PrimaryLocationCode, day of the week from date |
| Copyright            | IPTC   | CopyrightNotice                                                  |
| ALT Text             | XMP    | AltTextAccessibility                                             |
| Extended Description | XMP    | ExtDescrAccessibility                                            |

