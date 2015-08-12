
#import pyspark
from pyspark import SparkContext

class CCSpark(object):
    SC = None

    @classmethod
    def initSC(cls):
        if cls.SC is None:
            cls.SC = SparkContext('local', 'ClassCat NSM')

    @classmethod
    def getSC(cls):
        return cls.SC

        pass

    pass
