#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/11/4

' url handlers '

from coroweb import get, post
from models import User
import asyncio
from aiohttp import web

@get('/')
async def index(request):
    users = await User.findAll()
    # return web.Response(body=b'<h1>Awesome users</h1>', content_type='text/html', charset='UTF-8')
    return {
        '__template__': 'test.html',
        'users': users
    }