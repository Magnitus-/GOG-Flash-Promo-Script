GOG Flash Promo Script
======================

Script that warns you when important updates occur during GOG's flash promo.

It is meant to be used during a GOG flash promo and will be updated to deal with the specifics for each promo.

Requirements
------------

- Python (2.7 or 3.x): https://www.python.org/
- A browser

Executing the script
--------------------

In Windows, you can simply double-click on the script after installing Python.

Alternatively, you can type the following command on the command line (from the script's directory): python FlashPromoScript.py

Usage
-----

- Warning on game change

Execute the script and select option 1. An alarm will be triggered in a browser tab (will play an alarm youtube video) whenever the a game on promotion changes.

- Warning for specific games on promo

In the script's directory, create a file called patterns.txt that will contain a unique part of titles for all the games you are interested in (one title per line).

Example of a patterns.txt file:
Neverwinter Nights
Icewind Dale
Master of Orion
Master of Magic

Then, execute the script and select option 2. An alarm will be triggered in a browser tab (will play an alarm youtube video) whenever one of the games you are interested in appears on promotion.

Once a game you a looking for is found and the alarm is triggered, the script will exit, which will allow you to edit the patterns.txt file (and remove the game's title from the file if you got it) and start the script anew.


