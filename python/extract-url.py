from urllib.request import urlopen
from bs4 import BeautifulSoup
from requests import get
import os
import re
import sys

#Example:
#python extract-url.py "http://italianoperstranieri.loescher.it/archivio-di-grammatica.n445" ".pdf"

def extracurl(urlname):
	urldest = urlname[::-1]
	pos = urldest.find("/")
	urldest = urldest[pos+1::]
	urldest = urldest[::-1]
	return(urldest)

def extracfile(urlname):
	urlfilename = urlname[::-1]
	pos = urlfilename.find("/")
	urlfilename = urlfilename[:pos:1]
	urlfilename = urlfilename[::-1]
	return(urlfilename)

urlname = str(sys.argv[1])
extension = str(sys.argv[2])
urldest = extracurl(urlname)
urlfilename = extracfile(urlname)
os.system('md %s' % (urlfilename))
os.system('cd %s' % (urlfilename))

html = urlopen(urlname)
bsObj = BeautifulSoup(html.read(), 'html.parser')
for bsLine in bsObj.find_all('a'):
	link = bsLine.get('href')
	if link is not None:
		if link.find(extension) > 0:
			urldown = extracurl(link)
			filename = extracfile(link)
			if urldest != urldown and link.find("http:") < 0 and link.find("ftp:") < 0 and link.find("https:") < 0 and link.find("sftp:") < 0:
				os.system('wget --quiet --show-progress --directory-prefix=%s %s/%s/%s' % (urlfilename,urldest,urldown,filename))
			else:
				os.system('wget --quiet --show-progress --directory-prefix=%s %s' % (urlfilename,link))