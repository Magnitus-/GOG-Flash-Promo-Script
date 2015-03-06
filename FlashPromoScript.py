# Authors: Eric Vallee (eric_vallee2003@yahoo.ca); Stephen Phoenix; Jonathan Markevich
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
    def Convert(Input):
        return str(Input)
else:
    import urllib.request as urllib2
    import urllib.error
    ExceptionClass = urllib.error.URLError
    userInput = input
    def Convert(Input):
        return str(Input, encoding='utf-8')

VERBAL = True  # Set to True if you want feedback
ESCAPE = True  # Prevents the full power of regexes, but allows users to input special regex characters without escaping them
FILE_ALARM = False  #Triggers alarm from a downloaded file instead of a youtube video
BATCH_ALARM = True #Executes a batch file instead of the above alarms


class GameInfo(object):
    def __init__(self, title, price, fullPrice, discount, stock, stockLeft):
        self.title = title
        self.price = price
        self.fullPrice = fullPrice
        self.discount = discount
        self.stock = stock
        self.stockLeft = stockLeft

    def __repr__(self):
        return "GameInfo:{0},{1},{2},{3}".format(self.title, self.price,
                                                 self.fullPrice, self.discount)

    def __eq__(self, other):
        if isinstance(other, GameInfo):
            return self.title == other.title
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, GameInfo):
            return not self.__eq__(GameInfo)

    def __hash__(self):
        return hash(self.__repr__())

    def __str__(self):
        return ("{0: <30}    -{1: <2}%  ${2: <5} (${3})  {5}/{4}".format(
                self.getSafeTitle(), self.discount, self.price, self.fullPrice, self.stock, self.stockLeft))

    def getSafeTitle(self):
        return Convert(self.title.encode(sys.stdout.encoding, errors='replace'))


class InsomniaPromo(object):
    alarmUrl = "http://www.youtube.com/watch?v=FoX7vd30zq8"
    SoundFileUrl = "http://soundbible.com/grab.php?id=1550&type=wav"
    SoundFile = "Alarm.wav"
    batchPath = "./AlarmScript.sh"
	
    @staticmethod
    def _soundAlarm():
        SoundFile = InsomniaPromo.SoundFile
        SoundFileUrl = InsomniaPromo.SoundFileUrl
        batchPath = InsomniaPromo.batchPath
        if FILE_ALARM:
            if not(os.path.exists(SoundFile)):
                try:
                    req = urllib2.Request(url=SoundFileUrl)
                    descriptor = urllib2.urlopen(req)
                except ExceptionClass:
                    print(sys.exc_info()[:2])
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
        elif BATCH_ALARM & os.path.exists(batchPath):
            os.system(batchPath)
        else:
            webbrowser.open(InsomniaPromo.alarmUrl, new=2)

    @staticmethod
    def loadPatterns(filename):
        patterns = []

        try:
            with open(filename) as f:
                lines = f.readlines()
        except FileNotFoundError:
            print ('Error! "{0}" not found'.format(filename))
            raise e

        patternIndex = 0

        print ("Pattern List")
        print ("--------------------------")

        for line in lines:
            if line.endswith("\n"):
                line = line[:-1]

            if len(line):
                if ESCAPE:
                    for Special in ('.', '^', '$', '*', '+', '?', '\\', '{', '}', '[', ']', '(', ')', '|'):
                        line = line.replace(Special, "\\"+Special)
                patterns.append(line)
                print(line)
                patternIndex += 1

        print ("-------------------------------------------------------")
        return patterns

    def watchPatterns(self, patterns):
        self.patternList = self._processPatterns(patterns)

        while True:
            if VERBAL:
                print("\nWatching for games that match the pattern")

            reply = self._pollServer()
            if not len(reply):
                continue

            # Update and display current games
            self.games = self._getCurrentGames(reply)
            self._displayCurrentGames()

            # Check if current games match the patterns
            if self._match(reply, self.patternList):
                self._found()
                return
            else:
                self._notFound()

            time.sleep(self.delay)

    def watchNewGames(self):
        while True:
            if VERBAL:
                print("\nWatching for new games")

            reply = self._pollServer()
            if not len(reply):
                continue

            # Update and display current games
            self.games = self._getCurrentGames(reply)
            self._displayCurrentGames()

            # Check if one of current games has been changed
            if (not len(self.prevGames)):  # First run
                self.prevGames = self.games
            else:
                PreviousSet = set(self.prevGames)
                CurrentSet = set(self.games)
                if not(PreviousSet.issubset(CurrentSet) and PreviousSet.issuperset(CurrentSet)):
                    self.prevGames = self.games
                    self._newGamesAlert()

            time.sleep(self.delay)


class CurrentPromo(InsomniaPromo):
    def __init__(self, sourceUrl, delay):
        self.sourceUrl = sourceUrl
        self.delay = delay
        self.foundPattern = ""
        self.games = []
        self.prevGames = []

    def _newGamesAlert(self):
        if VERBAL:
            print("New games!")
            print("The script will now sound the alarm!")

        self._soundAlarm()

    def _found(self):
        if VERBAL:
            print("Found \""+self._getFoundPattern()+"\"!")
            print("The script will now sound the alarm!")

        self._soundAlarm()

        if VERBAL:
            print("Script will now end. Please, "
                  "remove the game from the PATTERNS list "
                  "if you bought it and restart the script.")

    def _notFound(self):
        if VERBAL:
            print("No game found. Will now sleep for " + str(self.delay) + " seconds.")

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

        body = Convert(descriptor.read())
        return body

    def _displayCurrentGames(self):
        try:
            print ("Seasoned: {0}".format(self.games[0]))
            print ("Fresh:    {0}".format(self.games[1]))
        except Exception:
            print ("Error displaying game title!")

    def _createGameInfo(self, replyDict, root):
        title = replyDict[root]['title']
        price, fullPrice = replyDict[root]['prices']['p']['USD']['1'].split(',')
        discount = replyDict[root]['discount']
        stock = replyDict[root]['stock']
        stockLeft = replyDict[root]['stockLeft']
        return GameInfo(title, price, fullPrice, discount, stock, stockLeft)

    def _getCurrentGames(self, body):
        replyDict = json.loads(body)
        currentGames = [self._createGameInfo(replyDict, 'oldschool'),
                        self._createGameInfo(replyDict, 'fresh')]
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
    try:
        main()
    except Exception:
        print(sys.exc_info()[:2])
        ask("")
