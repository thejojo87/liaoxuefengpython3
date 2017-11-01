#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/10/29

import logging;

logging.basicConfig(level=logging.INFO)

import asyncio
from aiohttp import web


def index(request):
    # 这里后面如果不加content——type那么就直接有一个下载界面。
    return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html', charset='UTF-8')


# init函数只运行一次，然后每次网络请求的时候另外一个协程调用create——server
async def init(loop):
    # 获取程序中的EventLoop，初始化，设置路由
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    # 因为asyncio是协程所以立马中断去执行下一个循环，然后继续执行下一句。
    # srv是生成器，init，srv只产生一次，每次的连接请求是srv生成的。所以这个函数就是返回一个生成器。
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server 开始于 127.0.0.1')
    return srv


# 获取EventLoop队列：
loop = asyncio.get_event_loop()
# 执行协程队列：把这个队列扔进去，因为init需要这个loop
loop.run_until_complete(init(loop))
loop.run_forever()
