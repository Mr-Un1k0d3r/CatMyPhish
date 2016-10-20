import urllib2
import sys
import time
import json
import random

version = "1.0"

if __name__ == "__main__":
	print "CatMyFish v%s - Search for available already categorized domain" % version
	print "Charles F. Hamilton - Mandiant 2016\n"

	try:
		from bs4 import BeautifulSoup
	except:
		print "bs4 not found"
		print "pip install beautifulsoup4"
		sys.exit(0)

	if len(sys.argv) < 2:
		print "Usage %s keyword\nOptions:\n\t-verbose\tMore verbose output" % sys.argv[0]
		sys.exit(0)
	
	hosts = []
	candidates = []
	verbose = False

	if "-verbose" in sys.argv:
		print "[+] Verbose mode enabled"
		verbose = True
		
	urls = {"expireddomain": {"get": "/domain-name-search/?q=", "post": "fdomainstart=&fdomain=&fdomainend=&flists%5B%5D=1&ftrmaxhost=0&ftrminhost=0&ftrbl=0&ftrdomainpop=0&ftrabirth_year=0&ftlds%5B%5D=2&button_submit=Apply+Filter&q=", "host": "https://www.expireddomains.net", "referer": "https://www.expireddomains.net/domain-name-search/?q=test&searchinit=1"}, \
"bluecoat": {"get": "/rest/categorization", "post": "url=", "host": "https://sitereview.bluecoat.com", "referer": None}, \
"instantdomain": {"get": "/services/all/", "post": None, "host": "https://instantdomainsearch.com"}}
	blacklisted = ["Phishing", "Suspicious", "Shopping", "Uncategorized"]
	keyword = sys.argv[1]
		
	request = urllib2.Request(urls["expireddomain"]["host"] + urls["expireddomain"]["get"] + keyword)
	request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
	request.add_header("Referer", urls["expireddomain"]["referer"])
	
	response = urllib2.urlopen(request, urls["expireddomain"]["post"] + keyword)
	html = BeautifulSoup(response.read(), "html.parser")
	
	tds = html.findAll("td", {"class": "field_domain"})
	for td in tds:
		for a in td.findAll("a", {"class": "namelinks"}):
			hosts.append(a.text)
	
	print "[+] (%d) domains found using the keyword \"%s\"" % (len(hosts), keyword)
	print "[+] BlueCoat categorization check may that several seconds. Bot check is pretty aggressive..."
		
	for host in hosts:
		request = urllib2.Request(urls["bluecoat"]["host"] + urls["bluecoat"]["get"])
		request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
		request.add_header("Origin", urls["bluecoat"]["host"])
		request.add_header("Referer", "https://sitereview.bluecoat.com/sitereview.jsp")
		request.add_header("X-Requested-With", "XMLHttpRequest")
		response = urllib2.urlopen(request, urls["bluecoat"]["post"] + host)
		try:
			json_data = json.loads(response.read())
			if json_data.has_key("errorType"):
				if json_data["errorType"] == "captcha":
					print "[-] BlueCoat blocked us :(" 
					sys.exit(0)
					
			cat = BeautifulSoup(json_data["categorization"], "html.parser")
			cat = cat.find("a")
			cat = cat.text
			if not cat in blacklisted:
				print "[+] Potential candidate: %s categorized as %s" % (host, cat)
				candidates.append(host)
			else:
				if verbose:
					print "[-] Rejected candidate: %s categorized as %s" % (host, cat)
		except:
			print "[-] Something when wrong"
		time.sleep(random.randrange(10,20))
		
	print "[+] (%d) candidates found using the keyword \"%s\"" % (len(candidates), keyword)
	
	# TODO check availability using godaddy API
	
	print "[+] Search completed"
