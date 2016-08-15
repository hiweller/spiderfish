# setwd('/Users/hannah/Dropbox/Westneat_Lab/OpenCV_Sandbox/spiderFish/')
args <- commandArgs(trailingOnly = TRUE)
setwd(paste(args[2], '/', args[1], sep=''))

library(rfishbase)
library(jsonlite)

# get list of species in family and species pictures downloaded
species <- species_list(Family = as.character(args[1])) # all species in family
pictures <- fromJSON(paste(args[1], '.json', sep='')) # JSON file for pictures downloaded
jsonSpecies <- unique(pictures$species) # unique species in the pictures downloaded

# find the overlap between species in family and species downloaded
# species in the species list but not the pictures list had no image available
# list as a dataframe
missingSpecies <- paste(args[2], '/', args[1], '/', args[1], '_missingPics.csv', sep="")
missingSpeciesDF <- data.frame(Species = species[(species %in% jsonSpecies)==FALSE])

# correlate picture names with species names
# picture naming convention is :
# first 2 letters of genus + 
# first 3 letters of species + 
# _ + (u, f, m, j as applicable for unidentified/female/male/juvenile) + number + .jpg
# just list out species and pic URL from JSON file and format as CSV
picSpecies <- pictures$species # list of species names from JSON file
picURL <- unlist(pictures$image_urls) # URLs from JSON file (some duplicates)
picURL <- substr(picURL, nchar(picURL)-11, nchar(picURL)) # get just relevant part of url

allPath <- dir(paste(args[2], '/', args[1], '/All', sep=""), pattern = '*.jpg')

speciesURL <- paste(args[2], '/', args[1], '/', args[1], '_speciesURLs.csv', sep="")

# only keep image urls that got used as permanent URLs in saving
speciesURLDF <- data.frame(Image=picURL, Species=picSpecies)
speciesURLDF <- speciesURLDF[picURL %in% allPath, ]
speciesURLDF <- speciesURLDF[order(speciesURLDF$Image),]


# of species that have a photograph, some probably only have a crummy photo (sorted into 'Fail')
# so let's get a list of species that didn't get a 'Pass' photo
# you'll have to decide whether you want the one(s) in the 'fail' category or not
passPath <- dir(paste(args[2], '/', args[1], '/Pass', sep=""), pattern = '*.jpg')
passSpecies <- speciesURLDF[speciesURLDF$Image %in% passPath,]

failPath <- dir(paste(args[2], '/', args[1], '/Fail', sep=""), pattern = '*.jpg')
failSpecies <- speciesURLDF[speciesURLDF$Image %in% failPath,]

failOnlyDF <- as.character(unique(failSpecies$Species)[(unique(failSpecies$Species) %in% unique(passSpecies$Species))==FALSE])
failOnlyDF <- data.frame(Species=failOnlyDF)
failOnly <- paste(args[2], '/', args[1], '/', args[1], '_failOnly.csv', sep="")

if (length(species[(species %in% jsonSpecies)==FALSE])==0){
  message("No missing species.")
} else {
  write.csv(x=missingSpeciesDF, row.names=FALSE, file=missingSpecies)
  message(paste(length(species[(species %in% jsonSpecies)==FALSE]),
                " species missing.", sep=""))
  message(paste("List of missing species is saved in ", missingSpecies, ".", sep=""))
}

write.csv(x=speciesURLDF, row.names=FALSE,
          file=speciesURL)
if (length(species[(species %in% jsonSpecies)==TRUE])==1) {
  message(paste(length(species[(species %in% jsonSpecies)==TRUE]),
                " species has at least one image.", sep=""))
} else {
  message(paste(length(species[(species %in% jsonSpecies)==TRUE]),
                " species have at least one image.", sep=""))
}

if (dim(failOnlyDF)[1]==0){
  message(paste("Of these species, all have at least one usable image passed by the image classifier.", sep=""))
} else if (dim(failOnlyDF)[1]==1){
  message(paste("Of these species, ", dim(failOnlyDF)[1], " species has only images rejected by the image classifier.", sep=""))
  message(paste("This species is stored in ", failOnly, ".", sep=""))
  write.csv(x=failOnlyDF, row.names=FALSE,
            file=failOnly)
} else {
  message(paste("Of these species, ", dim(failOnlyDF)[1], " species have only images rejected by the image classifier.", sep=""))
  message(paste("A list of these species is stored in ", failOnly, ".", sep=""))
  write.csv(x=failOnlyDF, row.names=FALSE,
            file=failOnly)
}

message(paste("Corresponding species and image names are saved in ", speciesURL, ".", sep=""))
