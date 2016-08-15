# spiderfish
Pipeline for downloading and sorting Fishbase images.

# About
Uses python and R to download all Fishbase images of a user-specified family, 
then sorts out standardized (full body lateral view, relatively uniform background) 
images for easy digitization. The pipeline follows 5 steps after you give it a fish family:

1) Downloads all images of that fish family that have confirmed identifications from Fishbase using Scrapy in python (http://scrapy.org/).

2) Sorts images into 'Pass' or 'Fail' categories based on regionalized color histogram indices, 
