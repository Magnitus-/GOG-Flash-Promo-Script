#Author: Eric Vallee (eric_vallee2003@yahoo.ca)
import urllib2
import time
import re
import webbrowser
import sys

Patterns = ["[Dd]eponia", "[Ff]latout"]
Alarm_url = "http://www.youtube.com/watch?v=FoX7vd30zq8"
GOG_ajax_url = 'http://www.gog.com/springinsomnia/ajax/getCurrentOffer'
Delay_between_requests = 4.0

def Warn():
	Pattern_list = [re.compile(Pattern) for Pattern in Patterns]
	while True:
		try:
			req = urllib2.Request(url=GOG_ajax_url)
			f = urllib2.urlopen(req)
		except urllib2.HTTPError:
			print sys.exc_info()[:2]
			continue
		except urllib2.URLError:
			print sys.exc_info()[:2]
			continue
		Reply = f.read()
		for Pattern in Pattern_list:
			Match = Pattern.search(Reply)
			if Match:
				webbrowser.open(Alarm_url, new=2)
				return
		time.sleep(Delay_between_requests)
		
Warn()