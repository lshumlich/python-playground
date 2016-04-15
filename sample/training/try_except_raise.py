"""

This gives an example of how technically try except raise work

"""
import traceback,sys


class MyError (Exception):
    None


def first_call():
    try_me()

def try_me():

    while True:
        print("Enter a Number between 1 - 10 :")
        number = input()
        i = int(number)
        if i > 10:
            raise MyError(number, " is greater than 10 dummy.")
        a = 1 / i
        print(a)


print("---With a try---.")
try:
    first_call()
except Exception as e:
    print("We have an except")
    # traceback.print_exc(file=sys.stdout)


print("---Without a try")
first_call()

