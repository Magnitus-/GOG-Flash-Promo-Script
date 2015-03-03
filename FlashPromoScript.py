# Author: Eric Vallee (eric_vallee2003@yahoo.ca)
# Modified by Stephen Phoenix
import time
import re
import webbrowser
import sys

if sys.version_info.major == 2:
    import urllib2 as urllib2
    ExceptionClass = urllib2.URLError
else:
    import urllib.request as urllib2
    import urllib.error
    ExceptionClass = urllib.error.URLError

VERBAL = True  # Set to True if you want feedback


def loadPatternFromFile():
    patterns = []

    with open("patterns.txt") as f:
        lines = f.readlines()

    patternIndex = 0

    for line in lines:
        if line.endswith("\n"):
            line = line[:-1]

        if len(line):
            patterns.append(line)
            print "{0:2}. {1}".format(patternIndex + 1, line)
            patternIndex += 1

    print "\n"
    return patterns


class InsomniaPromo2014(object):
    SourceURL = 'http://www.gog.com/springinsomnia/ajax/getCurrentOffer'
    Delay = 4.0  # 4 seconds

    @staticmethod
    def _ProcessPatterns(Patterns):
        return [re.compile(Pattern, re.IGNORECASE) for Pattern in Patterns]

    @staticmethod
    def _Match(Reply, Patterns):
        for Pattern in Patterns:
            Match = Pattern.search(Reply)
            if Match:
                return True
        return False


class LateWinterPromo2015(InsomniaPromo2014):
    SourceURL = 'http://www.gog.com/doublesomnia/getdeals'
    Delay = 10.0    # 10 seconds


class PromoWarner(LateWinterPromo2015):
    AlarmURL = "http://www.youtube.com/watch?v=FoX7vd30zq8"

    def __init__(self, Patterns):
        self.PatternList = self._ProcessPatterns(Patterns)

    def Warn(self):
        if VERBAL:
            print("Ready to poll the GOG server.")
        while True:
            if VERBAL:
                print("Polling the GOG server...")
            try:
                req = urllib2.Request(url=self.SourceURL)
                Descriptor = urllib2.urlopen(req)
            except ExceptionClass:
                print(sys.exc_info()[:2])
                time.sleep(self.Delay)
                continue
            Reply = str(Descriptor.read())
            if self._Match(Reply, self.PatternList):
                if VERBAL:
                    print("Game found! The script will now sound the alarm!")
                webbrowser.open(self.AlarmURL, new=2)
                if VERBAL:
                    print("Script will now end. Please, "
                          "remove the game from the PATTERNS list "
                          "if you bought it and restart the script.")
                return
            elif VERBAL:
                print("No game found. Will now sleep for " + str(self.Delay)
                      + " seconds.")
            time.sleep(self.Delay)


if __name__=='__main__':
    patterns = loadPatternFromFile()
    Warner = PromoWarner(patterns)
    Warner.Warn()
