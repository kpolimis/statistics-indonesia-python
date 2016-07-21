import requests

url = "http://sociology.morrisville.edu/readings/ANTH101/Anthropology-Introduction.pdf"
r = requests.get(url, stream = True)
chunk_size = int(requests.head(url).headers["content-length"])

with open ("anthroplogy.pdf", 'wb') as fd:
    for chunk in r.iter_content(chunk_size):
        fd.write(chunk)
