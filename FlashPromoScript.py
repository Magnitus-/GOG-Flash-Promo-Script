#Author: Eric Vallee (eric_vallee2003@yahoo.ca)
import time
import re
import webbrowser
import sys
import string

if sys.version_info.major==2:
    import urllib2 as urllib2
    ExceptionClass = urllib2.URLError
else:
    import urllib.request as urllib2
    import urllib.error
    ExceptionClass = urllib.error.URLError

PATTERNS = ["Original Sin", "Second Sky", "Tendry", "Time Force", "Gunthro", "Defender of the Crown", "Wasteland 2", "Ethan Carter", "Friendship and Madness", "Starpoint Gemini", "Door Kickers", "Wings!", "X-Wing", "Tie Fighter", "Knights of the old Republic", "Sam & Max", "Last Federation", "Heretic Kingdoms", "Space Rangers HD", "Double Dragon", "Lords of Xulima", "Battlefront", "Rogue Squadron", "Grim Fandango", "Republic Commando", "Apotheon", "Sunless Sea", "Mortal Kombat", "Escapists", "Felghana", "Ys Origin", "Chronicles+", "Unwritten Tales 2", "New 'N' Tasty", "Republique", "Shelter 2", "Hotline Miami 2", "Shovel Knight", "Where is my", "Banner Saga", "Lifeless Planet"]
VERBAL = True  #Set to True if you want feedback

class InsomniaPromo2014(object):
    SourceURL = 'http://www.gog.com/springinsomnia/ajax/getCurrentOffer'
    Delay = 4.0 #4 seconds

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
    Delay = 10.0    #10 seconds

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
                    print("Script will now end. Please, remove the game from the PATTERNS list if you bought it and restart the script.")
                return
            elif VERBAL:
                print("No game found. Will now sleep for "+str(self.Delay)+" seconds.")
            time.sleep(self.Delay)


if __name__=='__main__':
    Warner = PromoWarner(PATTERNS)
    Warner.Warn()   
