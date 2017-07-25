import urllib2
import os
import sys
import time
import json
import random

version = "1.0"

if __name__ == "__main__":
	print "CatMyFish v%s - Search for available already categorized domain" % version
	print "Mr.Un1k0d3r - RingZer0 Team 2016\n"

	try:
		from bs4 import BeautifulSoup
	except:
		print "[-] Fatal error: bs4 not found"
		print "pip install beautifulsoup4"
		sys.exit(0)

	if len(sys.argv) < 2:
		print "Usage %s keyword\nOptions:\n\t-verbose\tMore verbose output\n\t-exitone\tStop querying Symantec after first success\n\t-filename\tPull list from a file (-filename=path)" % sys.argv[0]
		sys.exit(0)
	
	hosts = []
	candidates = []
	keyword = ""
	verbose = False
	filename = None
	exitone = True if "-exitone" in sys.argv else False

	urls = {"expireddomain": {"get": "/domain-name-search/?q=", "post": "fdomainstart=&fdomain=&fdomainend=&flists%5B%5D=1&ftrmaxhost=0&ftrminhost=0&ftrbl=0&ftrdomainpop=0&ftrabirth_year=0&ftlds%5B%5D=2&button_submit=Apply+Filter&q=", "host": 
"https://www.expireddomains.net", "referer": "https://www.expireddomains.net/domain-name-search/?q=&searchinit=1"}, \
"bluecoat": {"get": "/rest/categorization", "post": "url=", "host": "https://sitereview.bluecoat.com", "referer": None}, \
"checkdomain": {"get": "/cgi-bin/checkdomain.pl?domain=", "post": None, "host": "http://www.checkdomain.com"}}
	# TODO: Need to add more to that list
	blacklisted = ["Phishing", "Web Ads/Analytics", "Suspicious", "Shopping", "Uncategorized", "Placeholders", "Pornography", "Spam", "Gambling", "Scam/Questionable/Illegal", " Malicious Sources/Malnets"]
	
	if "-verbose" in sys.argv:
		print "[+] Verbose mode enabled"
		verbose = True
		
	for item in sys.argv:
		if not item.find("-filename") == -1:
			filename = item.split("=")[1]
			if not os.path.exists(filename):
				print "[-] \"%s\" not found." % filename
				exit(0)
			break
			
	if filename == None:
                request = urllib2.Request(urls["expireddomain"]["host"])
                request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
                response = urllib2.urlopen(request)
                cookies =  "ExpiredDomainssessid=" + response.info().getheader("Set-Cookie").split("ExpiredDomainssessid=")[1].split(";")[0] + "; urih="
                cookies = cookies + response.info().getheader("Set-Cookie").split("urih=")[1].split(";")[0] + "; "

		keyword = sys.argv[1]
		request = urllib2.Request(urls["expireddomain"]["host"] + urls["expireddomain"]["get"] + keyword)
		request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
		request.add_header("Referer", urls["expireddomain"]["referer"])
		# the _pk_id is hardcoded for now
		request.add_header("Cookie", cookies + "_pk_ses.10.dd0a=*; _pk_id.10.dd0a=5abbbc772cbacfb2.1496158514.1.1496158514.1496158514")	
		response = urllib2.urlopen(request, urls["expireddomain"]["post"] + keyword)
		html = BeautifulSoup(response.read(), "html.parser")
		
		tds = html.findAll("td", {"class": "field_domain"})
		for td in tds:
			for a in td.findAll("a", {"class": "namelinks"}):
				hosts.append(a.text)
		
		print "[+] (%d) domains found using the keyword \"%s\"." % (len(hosts), keyword)
	
	else:
		for line in open(filename, "rb").readlines():
			hosts.append(line.strip())
		print "[+] (%d) domains loaded." % (len(hosts))
			
	print "[+] Symantec categorization check may take several minutes. Bot check is pretty aggressive..."
	
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
					print "[-] Symantec blocked us :(" 
					sys.exit(0)
								
			cat = BeautifulSoup(json_data["categorization"], "html.parser")
			cat = cat.find("a")
			cat = cat.text
			if not cat in blacklisted:
				print "[+] Potential candidate: %s categorized as %s." % (host, cat)
				candidates.append(host)
				if exitone:
					break
			else:
				if verbose:
					print "[-] Rejected candidate: %s categorized as %s." % (host, cat)
		except:
			print "[-] Something when wrong"
		time.sleep(random.randrange(10,20))
		
	print "[+] (%d) candidates found." % (len(candidates))

	for candidate in candidates:
		request = urllib2.Request(urls["checkdomain"]["host"] + urls["checkdomain"]["get"] + candidate.split(".")[0])
		request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
		request.add_header("Referer", urls["checkdomain"]["host"])
		response = urllib2.urlopen(request)
	
		if not response.read().find("is still available") == -1:
			print "[+] Awesome \"%s\" is categorized and available." % candidate
		
	print "[+] Search completed."
