import time
import asyncio
from aiohttp import web



class Hello(object):
    def __init__(self):
        self.xxx = 4
        print(self.xxx)
    print('ccc')
    pass

    def test(self):
        print('ddd')
        print(self.xxx)
# 二生三：创建实列
# hello = Hello()

# 三生万物：调用实例方法
# print(hello)

Hello.test(4)