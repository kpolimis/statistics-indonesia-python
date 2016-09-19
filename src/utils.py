import os
import re
import urllib
import nltk
import nltk.data
import pandas as pd
from bs4 import BeautifulSoup
from cStringIO import StringIO
from nltk.corpus import stopwords
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


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


def get_Istat_data():
    """
    Download Istat Household Budget Survey, unless already downloaded
    """
    download_if_needed('http://www.istat.it/en/files/2016/02/ISTAT_MFR_' +
                       'HBS_2014_IT1.zip',
                       'Istat_HBS_2014.zip')


def get_Sukarno_Bandung_speech():
    """
    Download President Sukarno Speech at
    the Opening of the Bandung Conference, April 18 1955
    """
    download_if_needed('http://www.cvce.eu/content/publication/2001/9/5/88d3' +
                       'f71c-c9f9-415a-b397-b27b8581a4f5/publishable_en.pdf',
                       'sukarno_bandung_speech.pdf')


def get_Sukarno_Jogjakarta_speech():
    """
    Download President Sukarno Speech at Jogjakarta, on 19th December 1961
    """
    download_if_needed('http://www.cvce.eu/content/publication/2001/9/5/88d3' +
                       'f71c-c9f9-415a-b397-b27b8581a4f5/publishable_en.pdf',
                       'sukarno_jogjakarta_speech.pdf')


def get_HBS_data():
    """
    Fetch pronto data (if needed) and extract trips as dataframe
    """
    get_Istat_data()
    zf = zipfile.ZipFile('Istat_HBS_2014.zip')
    file_handle = zf.open('FILENAME.csv')
    return pd.read_csv(file_handle)


def speech_to_wordlist(speech, remove_stopwords=False):
    # Function to convert a document to a sequence of words,
    # optionally removing stop words.  Returns a list of words.
    #
    #
    # 1. Remove non-letters
    speech = re.sub("[^a-zA-Z]", " ", speech)
    #
    # 3. Convert words to lower case and split them
    words = speech.lower().split()
    #
    # 4. Optionally remove stop words (false by default)
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    #
    # 5. Return a list of words
    return(words)


def speech_to_sentences(speech, tokenizer, remove_stopwords=False):
    # Function to split a speechinto parsed sentences. Returns a
    # list of sentences, where each sentence is a list of words
    #
    # 1. Use the NLTK tokenizer to split the paragraph into sentences
    # Download the punkt tokenizer for sentence splitting
    raw_sentences = tokenizer.tokenize(speech.strip())
    #
    # 2. Loop over each sentence
    sentences = []
    for raw_sentence in raw_sentences:
        # If a sentence is empty, skip it
        if len(raw_sentence) > 0:
            # Otherwise, call review_to_wordlist to get a list of words
            sentences.append(speech_to_wordlist(raw_sentence,
                             remove_stopwords))
    #
    # Return the list of sentences (each sentence is a list of words,
    # so this returns a list of lists
    return sentences


def to_xml(df, filename=None, mode='w'):
    def row_to_xml(row):
        xml = ['<item>']
        for i, col_name in enumerate(row.index):
            xml.append('  <field name="{0}">{1}</field>'.format(col_name,
                                                                row.iloc[i]))
        xml.append('</item>')
        return '\n'.join(xml)
    res = '\n'.join(df.apply(row_to_xml, axis=1))

    if filename is None:
        return res
    with open(filename, mode) as f:
        f.write(res)

pd.DataFrame.to_xml = to_xml


# Convenience functions for working with color ramps and bars
def colorbar_index(ncolors, cmap, labels=None, **kwargs):
    """
    This is a convenience function to stop you making off-by-one errors
    Takes a standard colourmap, and discretizes it,
    then draws a colour bar with correctly aligned labels
    """
    cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = plt.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))
    if labels:
        colorbar.set_ticklabels(labels)
    return colorbar


def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet.
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki],
                      colors_rgba[i, ki]) for i in xrange(N + 1)]

    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N,
                                                     cdict, 1024)


def convert_pdf_to_txt(path):
    """
    This function converts a .pdf file to text
    @path: file path to .pdf document

    from: http://stackoverflow.com/questions/26494211/
    extracting-text-from-a-pdf-file-using-pdfminer-in-python/26495057#26495057

    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text
