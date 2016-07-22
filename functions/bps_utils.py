import urllib
import os
import pandas as pd


def download_if_needed(URL, filename):
    """
    Download from URL to filename unless filename already exists
    """
    if os.path.exists(filename):
        print(filename, 'already exists')
        return
    else:
        print('downloading', filename)
        urllib.urlretrieve(URL, filename)


def get_education_data():
    """
    Download BPS education data, unless already downloaded
    """
    download_if_needed('http://data.go.id/dataset/58490386-5c56-410f-bdcc-57' +
                       'bf0d3cc35c/resource/2aa6278c-09c7-446e-bb37-67553870' +
                       '5163/download/processedjumlahpenduduktingkatpendidik' +
                       'anjeniskelaminkabupatensensus2010.csv',
                       'indonesia_education-country.csv')
