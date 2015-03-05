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

class InsomniaPromo(object):
    alarmUrl = "http://www.youtube.com/watch?v=FoX7vd30zq8"
    SoundFileUrl = "http://soundbible.com/grab.php?id=1550&type=wav"
    SoundFile = "Alarm.wav"
    batchPath = "./pushprowl.sh"

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
        elif BATCH_ALARM:
            os.system(batchPath)
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
        self.games = self._getCurrentGames(body)
        self.stock = self._getCurrentStock(body)
        print ("Seasoned: "+self.games[0])
        if VERBAL:
            print (" ("+`self.stock[0]`+"/"+`self.stock[2]`+")")
            
        print ("Fresh: "+self.games[1])
        if VERBAL:
            print (" ("+`self.stock[1]`+"/"+`self.stock[3]`+")\n")

        return body

    def _getCurrentGames(self, body):
        replyDict = json.loads(body)
        currentGames = [replyDict['oldschool']['title'], replyDict['fresh']['title']]
        return currentGames

    def _getCurrentStock(self, body):
        replyDict = json.loads(body)
        currentStock = [replyDict['oldschool']['stockLeft'],replyDict['fresh']['stockLeft'],
           replyDict['oldschool']['stock'],replyDict['fresh']['stock'],]
        return currentStock

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
