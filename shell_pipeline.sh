# SHELL SCRIPT OPTION FOR PIPELINE
#!/bin/bash

# 1) Change swd (line 10) to the absolute path on your computer where the spiderFish folder is stored.
# 3) Make sure script executable ($ chmod +x shell_pipeline.sh)
# 4) Run spiderFish ($ source shell_pipeline.sh)
# It will prompt you for the rest of the input
# ALTERNATIVE: see bash_profile_pipeline.sh

# swd = ABSOLUTE/PATH/TO/CLONED/REPO
swd=/Users/hannah/Dropbox/Westneat_Lab/spiderFish

# prompt fish family
echo -e "\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1  Fish family?"
read family

# prompt destination for results
echo "Folder destination?"
read fishPath

# make folder for storing all results
mkdir -p $fishPath/$family

# cd to that directory and store the absolute filepath (since relative filepath may be provided)
cd $fishPath
cwd=$(pwd)

# cd to directory where local spider is stored and initiate search
cd $swd/fishbase
echo -e "\xf0\x9f\x8e\xa3 Gone fishin'... \xf0\x9f\x8e\xa3"
sleep 1 # did I make it pause for a second so you have time to read the ‘Gone fishin’ with the fishing rod emoticons? you bet I did
scrapy crawl fish -a family=$family -o $family.json

# remove SHA1 tagged files/keep only the renamed ones
# this is janky, I know there's probably a way to say 'get rid of anything that is exactly 20 characters' but I futzed with it for ages and couldn't get it to work so this is fine for now…
find ./fishbase/output/full -type f -name "????????????????????*.*" -exec rm -rf {} \;

# move all downloaded images and output JSON file to results folder
mv ./fishbase/output/full/*.jpg $cwd/$family
rm ./fishbase/output/full/*.gif
mv $family.json $cwd/$family

# initiate image classification
python $swd/Sorting.py --dataset $cwd/$family

# make folder for storing unsorted copies of images and move images into it
mkdir $cwd/$family/All
mv $cwd/$family/*.jpg $cwd/$family/All

# reads JSON file and images in results folder and compares them to list of species on fishbase
	# output is up to 3 CSV files:

# 1) family_speciesURLs.csv gives the picture URL and the species it corresponds to (ex: caaur_u1.jpg = 'Carassius auratus').

# 2) family_missingPics.csv gives a list of any species for which no pictures are downloaded but which are listed as valid species on Fishbase (if 0, this file is not generated).

# 3) family_failOnly.csv gives a list of species for which any fishbase photos were rejected by the image classifier (if 0, this file is not generated).
Rscript $swd/speciesNames.R $family $cwd

# go to results directory and prompt for display of images that passed image classifier
cd $cwd
echo "Finished. Display results? (y/n)"
read response
case $response in
	y|Y) open $cwd/$family/Pass/* ;;
esac

echo -e "\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1  	\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1  	\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1  	\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1  	\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1  	\xf0\x9f\x90\x9f  \xf0\x9f\x90\xA0  \xf0\x9f\x90\xA1"
