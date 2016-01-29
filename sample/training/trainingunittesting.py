import os
import sys
import unittest

class Person(object):
    
    def __init__(self,n,a):
        self.name = n
        self.age = a
    def __str__(self):
        return self.name + ' is ' + str(self.age) + ' years old.'
    
    def birthday(self):
        self.age += 1


# Lets do a little test after unit testing... This is bad but explains the concept

class Person_Test(unittest.TestCase):
# Delete these methods and replace them wiht good testing methods.......
    def testStuff1(self):
        print('Running Person_Test.testStuff1')

    def testStuff2(self):
        print('Running Person_Test.testStuff2')

    def testStuff3(self):
        print('Running Person_Test.testStuff3')

# Delete this class. It was just showing an example.
class PersonWhatever_Test(unittest.TestCase):

    def testStuff1(self):
        print('Running PersonWhatever_Test.testStuff1')

print(__file__)
print(__name__)
print(os.path.basename(__file__))
print(os.path.basename(sys.argv[0]))

if __name__ == '__main__':
    unittest.main()
