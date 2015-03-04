# Authors: Eric Vallee (eric_vallee2003@yahoo.ca); Stephen Phoenix
import time
import re
import webbrowser
import sys
import os
import subprocess
import json

if sys.version_info.major == 2:
    import urllib2 as urllib2
    ExceptionClass = urllib2.URLError
    userInput = raw_input
else:
    import urllib.request as urllib2
    import urllib.error
    ExceptionClass = urllib.error.URLError
    userInput = input

VERBAL = True  # Set to True if you want feedback
FILE_ALARM = False

class InsomniaPromo(object):
    alarmUrl = "http://www.youtube.com/watch?v=FoX7vd30zq8"
    SoundFileUrl = "http://soundbible.com/grab.php?id=1550&type=wav"
    SoundFile = "Alarm.wav"
    
    @staticmethod
    def _soundAlarm():
        SoundFile = InsomniaPromo.SoundFile
        SoundFileUrl = InsomniaPromo.SoundFileUrl
        if FILE_ALARM:
            if not(os.path.exists(SoundFile)):
                try:
                    req = urllib2.Request(url=SoundFileUrl)
                    descriptor = urllib2.urlopen(req)
                except ExceptionClass:
                    print(sys.exc_info()[:2])
                    time.sleep(self.delay)
                    return
                soundFile = open(SoundFile,'wb')
                soundFile.write(descriptor.read())
                soundFile.close()
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", SoundFile])
            elif sys.platform == 'darwin':
                subprocess.call(["afplay",SoundFile])
            else:
                os.system("start "+SoundFile)
        else:
            webbrowser.open(InsomniaPromo.alarmUrl, new=2)
    
    @staticmethod
    def loadPatterns(filename):
        patterns = []
    
        with open(filename) as f:
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


class CurrentPromo(InsomniaPromo):
    def __init__(self, sourceUrl, delay):
        self.sourceUrl = sourceUrl
        self.delay = delay
        self.foundPattern = ""
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

    def watchPatterns(self, patterns):
        self.patternList = self._processPatterns(patterns)

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

        self._soundAlarm()

    def _found(self):
        if VERBAL:
            print("Found \"{0}\"!".format(self._getFoundPattern()))
            print("The script will now sound the alarm!")

        self._soundAlarm()

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

        body = str(descriptor.read())
        self.games = self._getCurrentGames(body)
        print ("Seasoned: {0}".format(self.games[0]))
        print ("Fresh: {0}\n".format(self.games[1]))

        return body

    def _getCurrentGames(self, body):
        replyDict = json.loads(body)
        currentGames = [replyDict['oldschool']['title'], replyDict['fresh']['title']]
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
    answer = userInput(message)
    return answer


def main():
    promo = CurrentPromo(sourceUrl="http://www.gog.com/doublesomnia/getdeals", delay=10.0)

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
            patterns = CurrentPromo.loadPatterns("patterns.txt")
            promo.watchPatterns(patterns)
        elif answer == "3":
            break

if __name__ == '__main__':
    main()
