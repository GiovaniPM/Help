from urllib.request import urlopen
from bs4 import BeautifulSoup
from requests import get
import re

def download(url, file_name):
	with open(file_name, "wb") as file:
		response = get(url)
		file.write(response.content)

#Input the url
#urlname = "https://docs.oracle.com/cd/B28728_01/jded/html/doclist.html"
#downpath = "https://docs.oracle.com/cd/B28728_01/jded"
#urlname = "http://italianoperstranieri.loescher.it/archivio-di-grammatica.n445"
#downpath = "http://italianoperstranieri.loescher.it/archivio-di-grammatica.n445"
#urlname = "https://docs.oracle.com/cd/E16582_01/index.htm"
#downpath = "https://docs.oracle.com/cd/"
#urlname = "https://docs.oracle.com/cd/B28730_01/jded/html/doclist.html"
#downpath = "https://docs.oracle.com/cd/B28730_01/jded"
urlname = "https://docs.oracle.com/cd/E12293_01/jded/html/doclist.html"
downpath = "https://docs.oracle.com/cd/E12293_01/jded"
#urlname = "https://support.microsoft.com/pt-br/help/13768/desktop-themes-featured"
#downpath = "https://support.microsoft.com/pt-br/help/13768/desktop-themes-featured"
extension = ".pdf"
html = urlopen(urlname)
bsObj = BeautifulSoup(html.read(), 'html.parser')
#In case of multiple panels
#print(bsObj)

total = 0
for bsLine in bsObj.find_all('a'):
	link = bsLine.get('href')
	if link is not None:
		if link.find(extension) > 0:
			total = total + 1

filenumber = 0
for bsLine in bsObj.find_all('a'):
	link = bsLine.get('href')
	if link is not None:
		if link.find(extension) > 0:
			filenumber = filenumber + 1
			filename = link[::-1]
			pos = filename.find("/")
			filename = filename[:pos:1]
			filename = filename[::-1]
			if urlname != downpath and link.find("http:") < 0 and link.find("ftp:") < 0 and link.find("https:") < 0 and link.find("sftp:") < 0:
				link = link.replace("..","")
				link = link.replace("//","/")
				link = downpath + link
			print("\033[0;37;40mDownloading ", filenumber, "of", total, "file: \033[1;33;40m", filename, "\033[0;37;40m from: \033[1;34;40m", link)
			download(link, filename)