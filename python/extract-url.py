from urllib.request import urlopen
from bs4 import BeautifulSoup
from requests import get
import os
import re
import sys

#Example:
#python extract-url.py "http://italianoperstranieri.loescher.it/archivio-di-grammatica.n445" ".pdf"

urlname = str(sys.argv[1])
urlfilename = urlname[::-1]
pos = urlfilename.find("/")
urldest = urlfilename[pos+1::]
urldest = urldest[::-1]
urlfilename = urlfilename[:pos:1]
urlfilename = urlfilename[::-1]
extension = str(sys.argv[2])
html = urlopen(urlname)
bsObj = BeautifulSoup(html.read(), 'html.parser')
os.system('md %s' % (urlfilename))
os.system('cd %s' % (urlfilename))

for bsLine in bsObj.find_all('a'):
	link = bsLine.get('href')
	if link is not None:
		if link.find(extension) > 0:
			filename = link[::-1]
			pos = filename.find("/")
			urldown = filename[pos+1::]
			urldown = urldown[::-1]
			filename = filename[:pos:1]
			filename = filename[::-1]
			if urldest != urldown and link.find("http:") < 0 and link.find("ftp:") < 0 and link.find("https:") < 0 and link.find("sftp:") < 0:
				os.system('wget --quiet --show-progress --directory-prefix=%s %s/%s/%s' % (urlfilename,urldest,urldown,filename))
			else:
				os.system('wget --quiet --show-progress --directory-prefix=%s %s' % (urlfilename,link))