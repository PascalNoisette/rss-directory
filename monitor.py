"""
    Custom Http handler
    Author: Pascal Noisette

"""

import os
import io
import optparse
import sys
import fcntl
from functools import partial
from shutil import copyfile


class Progress:

    def __init__(self, inc, total, file):
        self.current = 0
        self.previous = -1
        self.total = total
        self.inc = inc
        self.file = file

    def increment(self):
        self.current += self.inc
        percent = round(self.current/self.total*100)
        if self.previous < percent:
            self.previous = percent
            self.file.write("%d\n" % self.previous)

    def end(self):
        self.file.write("END")
        self.file.flush()

def monitor(func, implementation):
    def interceptor(*argv):

        # work with function func that yield something

        # strategy shall have the same argument as func and must return a tuple
        # - how much element will be returned for each yield
        # - the total element expected
        # - a file to write progress into
        #   the progress can be read from this file

        progress = Progress(*implementation(*argv))
        for i in func(*argv):
            progress.increment()
            yield i
        progress.end()
    return interceptor

