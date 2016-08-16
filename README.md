# spiderfish 0.0.1
Pipeline for downloading and sorting Fishbase images.

# About
Uses python and R to download all Fishbase images of a user-specified family, 
then sorts out standardized (full body lateral view, relatively uniform background) 
images for easy digitization. The pipeline follows 4 steps after you give it a fish family:

1) Downloads all images of that fish family that have confirmed identifications from Fishbase using Scrapy in python (http://scrapy.org/). Crawls species pages for photographs. See 'fishbase' folder.

2) Sorts images into 'Pass' or 'Fail' categories based on regionalized color histogram indices with OpenCV in python (http://opencv.org/). See 'Sorting.py' script. Image classification parameters are explained in 'Image Sorting' section.

3) Fetches a list of all species in family from Fishbase using the rfishbase package in R (https://github.com/ropensci/rfishbase).

4) Outputs list of species in family missing images from fishbase (if any), list of species whose only images were rejected by the image classifier (not good candidates for morphometrics/digitization), and a list of which species correspond to which image names. 

The results are stored in a directory specified by the user, in a 'FamilyName/' folder. The folder has 3 subfolders: 'Pass', 'Fail', and 'All', which contain images passed by the classifier, images rejected by the classifier, and duplicates of all images in case you don't care about the classification, respectively. The folder also contains a JSON file with all the image URLs, image names, and species names, as well as the generated CSV files.

# Usage
The pipeline is run through a simple shell script that just calls the steps above in the right order. There are two options for running it:

1) Add the 'spiderFish' command in 'bash_profile_pipeline.sh' to your bash profile (instructions are in the script).

2) Source the 'shell_pipeline.sh' script after making it executable (instructions are in the script).

The two options are identical other than how they're called -- personally, I prefer the bash profile option, since you can call it from any directory with the 'spiderFish' command instead of having to specify the exact filepath of the shell pipeline script.

Once called, spiderFish will prompt you for the name of a fish family (either all lowercase or first letter capitalized) and the destination for the results folder. For example:
```bash
user$ spiderFish
Fish family?
Chaetodontidae

Folder destination?
/Users/user/Desktop
```
If the family name is valid, scrapy will start crawling Fishbase for images, starting with something like this:

```bash
2016-08-16 11:52:34 [scrapy] INFO: Scrapy 1.1.1 started (bot: fishbase)
2016-08-16 11:52:34 [scrapy] INFO: Overridden settings: {'NEWSPIDER_MODULE': 'fishbase.spiders', 'FEED_URI': 'banjosidae.json', 'LOG_LEVEL': 'INFO', 'SPIDER_MODULES': ['fishbase.spiders'], 'BOT_NAME': 'fishbase', 'LOG_STDOUT': True, 'ROBOTSTXT_OBEY': True, 'FEED_FORMAT': 'json'}
2016-08-16 11:52:34 [scrapy] INFO: Enabled extensions:
['scrapy.extensions.feedexport.FeedExporter',
 'scrapy.extensions.logstats.LogStats',
...a bunch of other settings like that...
 'scrapy.pipelines.images.ImagesPipeline']
2016-08-16 12:55:47 [scrapy] INFO: Spider opened
2016-08-16 12:55:47 [scrapy] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2016-08-16 12:56:47 [scrapy] INFO: Crawled 209 pages (at 209 pages/min), scraped 80 items (at 80 items/min)
```
After 1-2 minutes of initializing, scrapy usually downloads images at about 50-100 images/minute from Fishbase. This is by far the longest step. Once it finishes, the image classifier and species tallies take a few seconds to run, followed by output like this:

```bash
2016-08-16 13:01:47 [scrapy] INFO: Closing spider (finished)
2016-08-16 13:01:47 [scrapy] INFO: Stored json feed (549 items) in: Chaetodontidae.json
2016-08-16 13:01:47 [scrapy] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 503515,
 'downloader/request_count': 1616,
...a bunch of other log stats...
 'scheduler/enqueued/memory': 517,
 'start_time': datetime.datetime(2016, 8, 16, 17, 55, 29, 882400)}
2016-08-16 13:01:47 [scrapy] INFO: Spider closed (finished)
Loading required package: methods
2 species missing.
List of missing species is saved in /Users/user/Desktop/Chaetodontidae/Chaetodontidae_missingPics.csv.

127 species have at least one image.
Of these species, 2 species have only images rejected by the image classifier.
A list of these species is stored in /Users/user/Desktop/Chaetodontidae_failOnly.csv.

Corresponding species and image names are saved in /Users/user/Desktop/Chaetodontidae_speciesURLs.csv.
Finished. Display results? (y/n)
```

Entering 'y' will display all the images in the 'Pass' folder.

You can also call different pieces of the pipeline separately, for example if you want to scrape images but not sort them, or sort images in a different folder, etc. This is most easily accomplished by copying the commands for these separate steps as specified in the pipeline scripts, and substituting your own arguments.

# Requirements
* Python 2.7+
* R 3.0+
* OpenCV 2.4+ ([A nice installation tutorial for OpenCV 3](http://www.pyimagesearch.com/2015/06/15/install-opencv-3-0-and-python-2-7-on-osx/), or just do `$ brew install opencv3 --with-contrib`)
* Scrapy 1.1+ ([Scrapy installation guide](http://doc.scrapy.org/en/latest/intro/install.html))
* Rfishbase ([CRAN documentation](https://cran.r-project.org/web/packages/rfishbase/rfishbase.pdf))

# Image Sorting

How is 'Sorting.py' deciding which images to pass, and which to fail? 




