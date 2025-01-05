# Photo Post Data

A script that generates text formated metadata for posting photos to photo sharing websites. I use Lightroom and have added an export preset for photo sharing websites. It runs this script against the exported JPEG and generates a text file in the same directory as the JPEG with the photo meta data.

One of the issues I had in moving from a photo sharing website like Flickr to a website like PixelFed is that Flickr displays all of the photo metadata for you. On PixelFed, you have to put all of the metadata you want to show in the description. Transcribing all of the metadata for every photo was
a pain, so I wrote a script to do it for me. Now I just paste the oputput of the script into the description box when posting a photo.

Example invocation:

> python3 /Users/tgoetz/Projects/Photography/PhotoPostData/photo_post_data.py --critique --gps --alttxt --copyright --file /Users/tgoetz/Downloads/_DSF8315.jpg --output /Users/tgoetz/Downloads/_DSF8315.txt

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

> python3 /Users/tgoetz/Projects/Photography/PhotoPostData/photo_post_data.py --exiftool "/opt/homebrew/bin/exiftool" --critique --alttxt --gps --copyright --file {NAME}.jpg --output {NAME}.txt
