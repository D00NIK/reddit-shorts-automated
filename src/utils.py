import os

from lxml import etree
from datetime import datetime, timedelta

class bcolors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def cleanDir(folder: str) -> None:
    """
    Deletes all files in a directory
    https://stackoverflow.com/a/185941
    """

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def removeHTMLTags(text: str) -> str:
    """
    Remove garbage html tags from a string
    https://www.slingacademy.com/article/python-ways-to-remove-html-tags-from-a-string/
    """

    parser = etree.HTMLParser()
    tree = etree.fromstring(text, parser)
    return etree.tostring(tree, encoding='unicode', method='text')

def replaceAll(text: str, dic: dict) -> str:
    """
    Replaces all occurences in a string from a dict
    https://stackoverflow.com/a/6117042
    """

    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def getFileContent(path: str) -> str:
    """
    Returns a file content as a string
    """

    with open(path, "r") as f:
        data = f.read()
    return data

def humanFormat(num):
    """
    Numbers to a more readable format, up to 1 milion
    """
    
    if (num >= 1000):
        num = str(int(num / 100))
        num = num[0:-1] + '.' + num[-1] + 'k'
    return str(num)

def relativeTime(date):
    """Take a datetime and return its "age" as a string.

    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.

    Make sure date is not in the future, or else it won't work.
    https://jonlabelle.com/snippets/view/python/relative-time-in-python
    """

    def formatn(n, s):
        """Add "s" if it's plural"""
        
        if n == 1:
            return "1 %s" % s
        elif n > 1:
            return "%d %ss" % (n, s)

    def qnr(a, b):
        """Return quotient and remaining"""

        return a / b, a % b

    class FormatDelta:

        def __init__(self, dt):
            now = datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds
            self.year, self.day = qnr(self.day, 365)
            self.month, self.day = qnr(self.day, 30)
            self.hour, self.second = qnr(self.second, 3600)
            self.minute, self.second = qnr(self.second, 60)

        def format(self):
            for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                n = int(getattr(self, period))
                if n > 0:
                    return '{0} ago'.format(formatn(n, period))
            return "just now"

    return FormatDelta(date).format()