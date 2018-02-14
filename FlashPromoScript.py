#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Original Author: Eric Vallee (eric_vallee@webificservices.com);
# Contributors: Stephen Phoenix; Jonathan Markevich

import time, re, webbrowser, sys, os, subprocess, json, datetime

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
ERROR_FORMAT = ("\n**************************************************"
                "\n{0}\n{1}\n{2}\n"
                "**************************************************\n")

class GameInfo(object):
    def __init__(self, title, price, fullPrice, discount, stock, stockLeft):
        self.title = title
        self.stockLeft = stockLeft
        self.discount = discount
        self.price = price
        self.fullPrice = fullPrice
        self.discount = discount
        self.stock = stock
        self.stockLeft = stockLeft
        self.stockLabel = 'duration'
        self.stockLeftLabel = 'duration left'

    def __repr__(self):
        return "GameInfo:{0},{1},{2},{3}".format(
            self.getSafeTitle(), self.price, self.fullPrice, self.discount)

    def __eq__(self, other):
        if isinstance(other, GameInfo):
            return self.getSafeTitle() == other.getSafeTitle()
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, GameInfo):
            return not self.__eq__(GameInfo)

    def __hash__(self):
        return hash(self.__repr__())

    def __str__(self):
        return "title: {title}, discount: -{discount}%, price: {price} (from {fullPrice}), {stockLabel}: {stock}, {stockLeftLabel}: {stockLeft}".format(
                title=self.getSafeTitle(), discount=self.discount,
                price=self.price, fullPrice=self.fullPrice,
                stock=self.stock, stockLeft=self.stockLeft,
                stockLabel=self.stockLabel, stockLeftLabel=self.stockLeftLabel)

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
        except Exception as e:
            print (ERROR_FORMAT.format(
                    'Error opening file "{0}"!'.format(filename),
                    type(e), str(e)))
            return None

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
            try:
                if self._match(reply, self.patternList):
                    self._found()
                    return
                else:
                    self._notFound()
            except Exception as e:
                print (ERROR_FORMAT.format(
                       "Error while comparing patterns!", type(e), str(e)))

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
            try:
                if (not len(self.prevGames)):  # First run
                    self.prevGames = self.games
                else:
                    PreviousSet = set(self.prevGames)
                    CurrentSet = set(self.games)
                    if not(PreviousSet.issubset(CurrentSet) and PreviousSet.issuperset(CurrentSet)):
                        self.prevGames = self.games
                        self._newGamesAlert()
            except Exception as e:
                print (ERROR_FORMAT.format(
                       "Error while checking a new game!", type(e), str(e)))

            time.sleep(self.delay)

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

    def _match(self, reply, patterns):
        self.foundPattern = ""

        for pattern in patterns:
            Match = pattern.search(reply)
            if Match:
                self.foundPattern = pattern.pattern
                return True
        return False

    def _processPatterns(self, patterns):
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

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

    def _getFoundPattern(self):
        return self.foundPattern

class CurrentPromo(InsomniaPromo):
    def __init__(self, sourceUrl, delay):
        self.sourceUrl = sourceUrl
        self.delay = delay
        self.foundPattern = ""
        self.games = []
        self.prevGames = []

    def _displayCurrentGames(self):
        try:
            index = 1
            for game in self.games:
                print "Game {0}: {1}".format(index, game)
                index+=1
        except Exception:
            print ("Error displaying game title!")

    def _createGameInfo(self, gameDict):
        title = gameDict['_embedded']['product']['title']

        currency = gameDict['_embedded']['product']['discount']['symbol']
        price = gameDict['_embedded']['product']['discount']['finalAmount'] + currency
        fullPrice = gameDict['_embedded']['product']['discount']['baseAmount'] + currency
        discount = gameDict['_embedded']['product']['discount']['discountPercentage']

        startDate = datetime.datetime.strptime( gameDict['startDate'], "%Y-%m-%dT%H:%M:%SZ" )
        endDate = datetime.datetime.strptime( gameDict['endDate'], "%Y-%m-%dT%H:%M:%SZ" )
        now = datetime.datetime.strptime( gameDict['now'], "%Y-%m-%dT%H:%M:%SZ" )

        stock = endDate - startDate
        stockLeft = endDate - now
        return GameInfo(title=title, price=price, fullPrice=fullPrice, discount=discount, stock=stock, stockLeft=stockLeft)

    def _getCurrentGames(self, body):
        replyDict = json.loads(body)
        try:
            currentGames = [self._createGameInfo(gameDict) for gameDict in replyDict['_embedded']['items']]
        except Exception as e:
            print (ERROR_FORMAT.format(
                   "Error while converting server info!", type(e), str(e)))
            currentGames = []
        return currentGames


def ask(message):
    answer = userInput(message)
    return answer

def main():
    promo = CurrentPromo(sourceUrl="https://www.gog.com/flashDealsSets/14674", delay=5.0)

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
            if not patterns:
                continue
            promo.watchPatterns(patterns)
        elif answer == "3":
            break

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print (ERROR_FORMAT.format("Error!", type(e), str(e)))
        ask("")
