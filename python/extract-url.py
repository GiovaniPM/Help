from urllib.request import urlopen
from bs4 import BeautifulSoup
from requests import get
import os
import re
import sys

#Example:
#python extract-url.py "http://italianoperstranieri.loescher.it/archivio-di-grammatica.n445" ".pdf"

def extracurl(urlname):
	strinv = urlname[::-1]
	pos = strinv.find("/")
	strinv = strinv[pos+1::]
	return(strinv[::-1])

def extracfile(urlname):
	strinv = urlname[::-1]
	pos = strinv.find("/")
	strinv = strinv[:pos:1]
	return(strinv[::-1])

urlname = str(sys.argv[1])
extension = str(sys.argv[2])
urlsite = extracurl(urlname)
filsite = extracfile(urlname)
os.system('md %s' % (filsite))
os.system('cd %s' % (filsite))

html = urlopen(urlname)
bsObj = BeautifulSoup(html.read(), 'html.parser')
for bsLine in bsObj.find_all('a'):
	link = bsLine.get('href')
	if link is not None:
		if link.find(extension) > 0:
			urldown = extracurl(link)
			fildown = extracfile(link)
			if urlsite != urldown and link.find("http:") < 0 and link.find("ftp:") < 0 and link.find("https:") < 0 and link.find("sftp:") < 0:
				print('wget --quiet --show-progress --directory-prefix=%s %s/%s/%s' % (filsite,urlsite,urldown,fildown))
				os.system('wget --quiet --show-progress --directory-prefix=%s %s/%s/%s' % (filsite,urlsite,urldown,fildown))
			else:
				print('wget --quiet --show-progress --directory-prefix=%s %s' % (filsite,link))
				os.system('wget --quiet --show-progress --directory-prefix=%s %s' % (filsite,link))