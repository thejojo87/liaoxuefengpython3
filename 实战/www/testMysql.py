#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/11/1

# 这是测试代码
import orm
# import models
from models import User
import asyncio
import sys
import logging

async def test():
    # 这就是连接代码，生成pool就会自动连接，但是首先要生成数据库才行
    await orm.create_pool(loop=loop, host='localhost', port=3306,
        user='root', password='password', db='awesome')
    print('test')
    user = User(name='tes', email='test7aasssa3ss5537@test.com', passwd='test', image='about:ddblank')
    # print(user)
    await user.save()
    r = await User.find('11')
    print(r)
    r = await User.findAll()
    print(1, r)
    r = await User.findAll(name='tes')
    print(2, r)
    await orm.destroy_pool()


# 获取EventLoop队列：
loop = asyncio.get_event_loop()
# 执行协程队列：把这个队列扔进去，因为init需要这个loop
loop.run_until_complete(test())
loop.close()
if loop.is_closed():
    sys.exit(0)
