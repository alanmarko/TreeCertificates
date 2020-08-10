"""
ProgressBar.py

ProgressBar.py implement a simple class for showing a progress bar inside of a terminal application
"""

import sys

class ProgressBar:
    def printProgress(self,i, count):
        percent=(int)((i/count)*100)
        percent=min(percent,100)
        sys.stdout.write('\r')
        sys.stdout.write("[%-100s] %d%%" % ('■' * percent, 1 * percent))
        sys.stdout.flush()
        #sleep(0.02)
        #if percent == 100:
            #print()

    def start(self):
        self.printProgress(0,100)

    def finish(self):
        self.printProgress(100,100)
        print()