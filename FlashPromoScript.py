# Author: Eric Vallee (eric_vallee2003@yahoo.ca)
# Modified by Stephen Phoenix
import time
import re
import webbrowser
import sys

if sys.version_info.major == 2:
    PYTHON2 = True
    import urllib2 as urllib2
    ExceptionClass = urllib2.URLError
else:
    PYTHON2 = False
    import urllib.request as urllib2
    import urllib.error
    ExceptionClass = urllib.error.URLError

VERBAL = True  # Set to True if you want feedback


def loadPatternFromFile():
    patterns = []

    with open("patterns.txt") as f:
        lines = f.readlines()

    patternIndex = 0

    print ("Pattern List")
    print ("--------------------------")

    for line in lines:
        if line.endswith("\n"):
            line = line[:-1]

        if len(line):
            patterns.append(line)
            print ("{0:2}. {1}".format(patternIndex + 1, line))
            patternIndex += 1

    print ("-------------------------------------------------------")
    return patterns


class InsomniaPromo(object):
    def __init__(self, sourceUrl):
        self.sourceUrl = sourceUrl
        self.delay = 10.0  # 10 seconds
        self.foundPattern = ""
        self.alarmUrl = "http://www.youtube.com/watch?v=FoX7vd30zq8"
        self.games = []
        self.prevGames = []

    def watchNewGames(self):
        while True:
            if VERBAL:
                print("\nWatching for new games")

            reply = self._pollServer()
            if not len(reply):
                continue

            if (not len(self.prevGames)):  # First run
                self.prevGames = self.games
            elif (self.games[0] != self.prevGames[0] or
                    self.games[1] != self.prevGames[1]):
                self.prevGames = self.games
                self._newGamesAlert()

            time.sleep(self.delay)

    def watchPatterns(self, patterns, delay):
        self.patternList = self._processPatterns(patterns)
        self.delay = delay

        while True:
            if VERBAL:
                print("\nWatching for games that match the pattern")

            reply = self._pollServer()
            if not len(reply):
                continue

            if self._match(reply, self.patternList):
                self._found()
                return
            else:
                self._notFound()

            time.sleep(self.delay)

    def _newGamesAlert(self):
        if VERBAL:
            print("New games!")
            print("The script will now sound the alarm!")

        webbrowser.open(self.alarmUrl, new=2)

    def _found(self):
        if VERBAL:
            print("Found \"{0}\"!".format(self._getFoundPattern()))
            print("The script will now sound the alarm!")

        webbrowser.open(self.alarmUrl, new=2)

        if VERBAL:
            print("Script will now end. Please, "
                  "remove the game from the PATTERNS list "
                  "if you bought it and restart the script.")

    def _notFound(self):
        if VERBAL:
            print("No game found. Will now sleep for " + str(self.delay)
                  + " seconds.")

    def _processPatterns(self, patterns):
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def _pollServer(self):
        if VERBAL:
                print(".....................................................")
        try:
            req = urllib2.Request(url=self.sourceUrl)
            descriptor = urllib2.urlopen(req)
        except ExceptionClass:
            print(sys.exc_info()[:2])
            time.sleep(self.delay)
            return ""

        s = str(descriptor.read())
        self.games = self._getCurrentGames(s)
        print ("Seasoned: {0}".format(self.games[0]))
        print ("Fresh: {0}\n".format(self.games[1]))

        return s

    def _getCurrentGames(self, s):
        TITLE = "\"title\":"
        currentGames = []

        strs = s.split("\"fresh\":{\"id\"")

        for i in range(2):
            title = strs[i].find(TITLE)
            start = strs[i].find("\"", title + len(TITLE))
            end = strs[i].find("\"", start + 1)
            name = strs[i][start + 1: end]
            currentGames.append(name)

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


def ask(message):
    if PYTHON2:
        answer = raw_input(message)
    else:
        answer = input(message)

    return answer


def main():
    promo = InsomniaPromo("http://www.gog.com/doublesomnia/getdeals")

    while (True):
        print ("\nGOG Flash Promo Watcher")
        print ("-------------------------------------")
        print ("  1. Watch for new games")
        print ("  2. Watch for games that match the patterns")
        print ("  3. Quit\n")
        answer = ask("Choose: ")

        if answer == "1":
            promo.watchNewGames()
        elif answer == "2":
            patterns = loadPatternFromFile()
            promo.watchPatterns(patterns, delay=10)
        elif answer == "3":
            break

if __name__ == '__main__':
    main()
