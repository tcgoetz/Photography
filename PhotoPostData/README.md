# Photo Post Data

A script that generates text formated metadata for posting photos to photo sharing websites. I use Lightroom and have added an export preset for photo sharing websites. It runs this script against the exported JPEG and generates a text file in the same directory as the JPEG with the photo meta data.

Example invocation:

> python3 /Users/tgoetz/Projects/Photography/PhotoPostData/photo_post_data.py --critique --gps --file /Users/tgoetz/Downloads/_DSF8315.jpg --output /Users/tgoetz/Downloads/_DSF8315.txt

Example output:

> Foggy Morning on the Marsh
> Mark's Cove, Wareham, Massachusetts, United States
> Photo location: https://www.openstreetmap.org/#map=17/41.736578433333335/-70.73129821333333
> Taken on 2024-12-29 10:28:40 with Fuji 10-24mm F4 on X-H2 with exposure 1/105s @ f/8.0 @ 10.0mm @ 200 ISO
> 
> Critiques welcome. Thanks for taking the time to look at my photo.
> 
> #photography #fog #LandscapePhotography #ocean #saltmarsh #weather #BuzzardsBay #photocritique #blackandwhitephotography

Integrating the Script into Lightroom

I have a export preset in Lightroom that uses Jeffrey Friedl's ["Run Any Command"](https://regex.info/blog/lightroom-goodies/run-any-command) plugin to run the script after the export. This is the template I use with "Run Any Command":

> python3 /Users/tgoetz/Scripts/photo_post_data.py --critique --gps --file {NAME}.jpg --output {NAME}.txt
