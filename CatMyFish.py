import urllib2
import os
import sys
import time
import json
import random
import argparse

version = "1.0"


def get_hosts_from_keywords(keywords):
    """
    Iterates over all the given keywords and grabs all expired hosts matching the keyword
    :param keywords: keywords search expireddomains.net for
    :return: hosts matching the searched keywords
    """
    hosts = []
    for keyword in keywords:
        request = urllib2.Request(urls["expireddomain"]["host"])
        request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
        response = urllib2.urlopen(request)
        request = urllib2.Request(urls["expireddomain"]["host"] + urls["expireddomain"]["get"] + keyword)
        request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
        request.add_header("Referer", urls["expireddomain"]["referer"])
        # the _pk_id is hardcoded for now
        request.add_header("Cookie",
                           "_pk_ses.10.dd0a=*; _pk_id.10.dd0a=5abbbc772cbacfb2.1496158514.1.1496158514.1496158514")
        response = urllib2.urlopen(request, urls["expireddomain"]["post"] + keyword)
        html = BeautifulSoup(response.read(), "html.parser")

        tds = html.findAll("td", {"class": "field_domain"})
        tmp_hosts = []
        for td in tds:
            for a in td.findAll("a", {"class": "namelinks"}):
                tmp_hosts.append(a.text)

        print "[+] (%d) domains found using the keyword \"%s\"." % (len(tmp_hosts), keyword)
        hosts.extend(tmp_hosts)
    if len(keywords) > 1:
        print  "[+] (%d) domains found using (%d) keywords." % (len(hosts), len(keywords))
    return hosts


def get_category(host):
    """
    Gets the Symantec category for a given host.
    :param host: The host for which to check the category
    :return: the category for the host
    """
    request = urllib2.Request(urls["bluecoat"]["host"] + urls["bluecoat"]["get"])
    request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0")
    request.add_header("Origin", urls["bluecoat"]["host"])
    request.add_header("Referer", "https://sitereview.bluecoat.com/lookup")
    request.add_header("Content-Type", "application/json; charset=utf-8")
    response = urllib2.urlopen(request, urls["bluecoat"]["post"].replace("[URL]", host))
    try:
        json_data = json.loads(response.read())

        if json_data.has_key("errorType"):
            if json_data["errorType"] == "captcha":
                print "[-] Symantec blocked us :("
                sys.exit(0)
        return json_data["categorization"][0]["name"]
    except:
        print "[-] Something when wrong, unable to get category for %s" % host


if __name__ == "__main__":
    print "CatMyFish v%s - Search for available already categorized domain" % version
    print "Mr.Un1k0d3r - RingZer0 Team 2016\n"

    try:
        from bs4 import BeautifulSoup
    except:
        print "[-] Fatal error: bs4 not found"
        print "Please run: pip install beautifulsoup4"
        sys.exit(0)

    hosts = []
    candidates = []
    f = None
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="More verbose output", action="store_true")
    parser.add_argument("-e", "--exitone", help="Stop querying Symantec after first success", action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--filename", help="Loads domains to check from a text file, instead of searching",
                       type=str)
    parser.add_argument("-o", "--output", type=str, help="Write unregistered, categorized domains to a file.")
    group.add_argument("keywords", help="Keyword to use when search for expired domains", nargs='*', default=[])
    args = parser.parse_args()

    verbose = args.verbose
    exitone = args.exitone
    keywords = args.keywords
    domain_file = args.filename
    output_file = args.output

    urls = {"expireddomain": {"get": "/domain-name-search/?q=",
                              "post": "fdomainstart=&fdomain=&fdomainend=&flists%5B%5D=1&ftrmaxhost=0&ftrminhost=0&ftrbl=0&ftrdomainpop=0&ftrabirth_year=0&ftlds%5B%5D=2&button_submit=Apply+Filter&q=",
                              "host":
                                  "https://www.expireddomains.net",
                              "referer": "https://www.expireddomains.net/domain-name-search/?q=&searchinit=1"}, \
            "bluecoat": {"get": "/resource/lookup", "post": '{"url":"[URL]","captcha":""}', "host": "https://sitereview.bluecoat.com",
                         "referer": None}}
    # TODO: Need to add more to that list
    blacklisted = ["Phishing", "Web Ads/Analytics", "Suspicious", "Shopping", "Uncategorized", "Placeholders",
                   "Pornography", "Spam", "Gambling", "Scam/Questionable/Illegal", " Malicious Sources/Malnets"]

    if args.verbose:
        print "[+] Verbose mode enabled"

    if args.filename and not os.path.exists(domain_file):
        print "[-] \"%s\" not found." % domain_file
        exit(0)

    if not args.filename:
        hosts = get_hosts_from_keywords(keywords)
    else:
        for line in open(domain_file, "rb").readlines():
            hosts.append(line.strip())
        print "[+] (%d) domains loaded." % (len(hosts))

    print "[+] Symantec categorization check may take several minutes. Bot check is pretty aggressive..."

    for host in hosts:
        cat = get_category(host)
        if not cat in blacklisted:
            print "[+] Potential candidate: %s categorized as %s." % (host, cat)
            candidates.append(host)
            if exitone:
                break
        else:
            if verbose:
                print "[-] Rejected candidate: %s categorized as %s." % (host, cat)
        time.sleep(random.randrange(10, 20))

    print "[+] (%d) candidates found." % (len(candidates))

    if output_file:
        f = open(output_file, "w")
        for candidate in candidates:
            f.write(candidate + "\n")

    print "[+] Search completed."
    if output_file:
        f.close()
