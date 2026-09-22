class Uppercase:
    def getstring(self):
        self.text=input()
    def printString(self):
        print(self.text.upper())

obj = Uppercase()
obj.getstring()
obj.printString()