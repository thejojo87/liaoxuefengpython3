import time
import asyncio
from aiohttp import web


class Student(object):
    def __init__(self, name):
        self.name = name
        print(self.name)

    def __call__(self):
        print('My name is %s.' % self.name)


# a = Student('99')
Student('00')()

