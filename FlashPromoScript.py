#Author: Eric Vallee (eric_vallee2003@yahoo.ca)
import urllib2
import time
import re
import webbrowser
import sys
from HTMLParser import HTMLParser
import string

PATTERNS = ["Flatout", "Master of Orion"]

class InsomniaPromo2014(object):
	SourceURL = 'http://www.gog.com/springinsomnia/ajax/getCurrentOffer'
	Delay = 4.0	#4 seconds

	@staticmethod
	def _ProcessPatterns(Patterns):
		return [re.compile(Pattern) for Pattern in Patterns]

	@staticmethod
	def _Match(Reply, Patterns):
		for Pattern in Patterns:
			Match = Pattern.search(Reply)
			if Match:
				return True
		return False

class SummerPromo2014(object):
	SourceURL = 'http://www.gog.com'
	Delay = 300.0	#5 minutes

	class SummerPromo2014Parser(HTMLParser):
		def Initialize(self, Patterns):
			self.Patterns = Patterns
			self.FoundPattern = False
			self.PromoDivs = 0
		def handle_starttag(self, Tag, Attributes):
			if self.PromoDivs == 0 and Tag == "div":
				for Attribute in Attributes:
					if Attribute[0]=="class" and Attribute[1]=="flash-deals":
						self.PromoDivs = self.PromoDivs + 1
			elif self.PromoDivs > 0 and Tag=="div":
				self.PromoDivs = self.PromoDivs + 1
				for Attribute in Attributes:
					if Attribute[0]=="data-gameindex":
						for Pattern in self.Patterns:
							Match = Pattern.search(Attribute[1])
							if Match:
								self.FoundPattern = True
				#print "Encountered a start tag:", Tag
				#print "With attributes", Attributes
		def handle_endtag(self, Tag):
			if self.PromoDivs > 0 and Tag == "div":
				self.PromoDivs = self.PromoDivs - 1
				#print "Encountered an end tag :", Tag

	@staticmethod
	def _ProcessPatterns(Patterns):
		return [re.compile(string.lower(string.replace(Pattern, " ", "_"))) for Pattern in Patterns]
		
	@staticmethod
	def _Match(Reply, Patterns):
		Parser = SummerPromo2014.SummerPromo2014Parser()
		Parser.Initialize(Patterns)
		Parser.feed(Reply)
		return Parser.FoundPattern
			

class PromoWarner(SummerPromo2014):
	AlarmURL = "http://www.youtube.com/watch?v=FoX7vd30zq8"
	def __init__(self, Patterns):
		self.PatternList = self._ProcessPatterns(Patterns)
		
	def Warn(self):
		while True:
			try:
				req = urllib2.Request(url=self.SourceURL)
				Descriptor = urllib2.urlopen(req)
			except urllib2.HTTPError:
				print sys.exc_info()[:2]
				continue
			except urllib2.URLError:
				print sys.exc_info()[:2]
				continue
			Reply = Descriptor.read()
			if self._Match(Reply, self.PatternList):
				webbrowser.open(self.AlarmURL, new=2)
				return
			time.sleep(self.Delay)


if __name__=='__main__':
	Warner = PromoWarner(PATTERNS)
	Warner.Warn()	
