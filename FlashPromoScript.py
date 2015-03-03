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

    print "Pattern List"
    print "--------------------------"

    for line in lines:
        if line.endswith("\n"):
            line = line[:-1]

        if len(line):
            patterns.append(line)
            print "{0:2}. {1}".format(patternIndex + 1, line)
            patternIndex += 1

    print "-------------------------------------------------------"
    return patterns


class InsomniaPromo(object):
    def __init__(self, sourceUrl):
        self.sourceUrl = sourceUrl
        self.delay = 10.0  # 10 seconds
        self.foundPattern = ""
        self.alarmUrl = "http://www.youtube.com/watch?v=FoX7vd30zq8"

    def watch(self, patterns, delay):
        self.patternList = self._processPatterns(patterns)
        self.delay = delay

        if VERBAL:
            print("Ready to poll the GOG server.")

        while True:
            reply = self._pollServer()
            if not len(reply):
                continue

            if self._match(reply, self.patternList):
                self._found()
            else:
                self._notFound()

            time.sleep(self.delay)

    def _found(self):
        if VERBAL:
            print("Found \"{0}\"!".format(self._getFoundPattern()))
            print("The script will now sound the alarm!")

        webbrowser.open(self.alarmUrl, new=2)

        if VERBAL:
            print("Script will now end. Please, "
                    "remove the game from the PATTERNS list "
                    "if you bought it and restart the script.")
        return

    def _notFound(self):
        if VERBAL:
            print("No game found. Will now sleep for " + str(self.delay)
                  + " seconds.")

    def _processPatterns(self, patterns):
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def _pollServer(self):
        if VERBAL:
                print("Polling the GOG server...")
        try:
            req = urllib2.Request(url=self.sourceUrl)
            descriptor = urllib2.urlopen(req)
        except ExceptionClass:
            print(sys.exc_info()[:2])
            time.sleep(self.delay)
            return ""

        s = str(descriptor.read())
        games = self._getCurrentGames(s)
        print "Seasoned: {0}".format(games[0])
        print "Fresh: {0}\n".format(games[1])

        return s

    def _getCurrentGames(self, s):
        TITLE = "\"title\":"
        currentGames = []

        strs = s.split("\"fresh\":{\"id\"")

        for i in range(2):
            title = strs[i].find(TITLE)
            start = strs[i].find("\"", title + len(TITLE))
            end = strs[i].find("\"", start + 1)
            currentGames.append(strs[i][start + 1: end])

        return currentGames

    def _match(self, reply, patterns):
        self.foundPattern = ""

        for pattern in patterns:
            Match = pattern.search(reply)
            if Match:
                self.foundPattern = pattern.pattern
                return True
        return False

    def _getFoundPattern(self):
        return self.foundPattern

if __name__ == '__main__':
    patterns = loadPatternFromFile()
    promo = InsomniaPromo("http://www.gog.com/doublesomnia/getdeals")
    promo.watch(patterns, delay=10)
