class Looper():

    def __init__(self,count):
        self.count = count
    
    def incCount(self,count):
        self.count += 1 

    def getCount(self):
        return self.count