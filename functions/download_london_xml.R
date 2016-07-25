#! /usr/bin/Rscript
#http://stackoverflow.com/questions/23584514/error-xml-content-does-not-seem-to-be-xml-r-3-1-0

#' downloads XML FDA Recalls Data Set 
#' parses XML to .csv format for analysis
if(!"RCurl" %in% installed.packages()) {
  install.packages("RCurl")
}


if(!"XML" %in% installed.packages()) {
  install.packages(c("XML"))
}

library(RCurl)
library(XML)

fileURL <- "https://raw.githubusercontent.com/data-navigator/python-ie-gis-presentation/master/data/london_20131229.xml"
xml_data <- getURL(fileURL)

## Parse XML
doc <- xmlTreeParse(xml_data, useInternalNodes = TRUE)

## Write to XML
write.csv(dat, "processed/FDA_recalls.csv", row.names = FALSE)
saveXML(doc, "london.xml")
