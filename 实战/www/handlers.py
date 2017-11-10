#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/11/4

' url handlers '

from coroweb import get, post
from models import User, Blog, Comment, next_id
import asyncio
from aiohttp import web
import time
from apis import APIValueError, APIError
import hashlib
import logging
from config import configs
import json

# @get('/')
# async def index(request):
#     users = await User.findAll()
#     # users = None
#     # return web.Response(body=b'<h1>Awesome users</h1>', content_type='text/html', charset='UTF-8')
#     return {
#         '__template__': '__base__.html',
#         'users': users
#     }

# Day 8 前端测试

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


# 根据用户信息拼接一个cookie字符串


def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    # 过期时间是当前时间+设置的有效时间
    expires = str(int(time.time() + max_age))
    # 构建cookie存储的信息字符串
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    # 用-隔开，返回
    return '-'.join(L)


@get('/')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore etLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et ddolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    # users = None
    # return web.Response(body=b'<h1>Awesome users</h1>', content_type='text/html', charset='UTF-8')
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

@get('/api/users')
async def api_get_users():
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '********'
    return dict(users=users)


# 用户注册
@get('/register')
async def register():
    return {
        '__template__': 'register.html'
    }

# 注册时候检查重复邮箱和用户名
@get('/register/checkSameItem')
async def register_check_same_item(*, item, searchValue):
    users = await User.findAll(item + "=?", [searchValue])
    if len(users) > 0:
        raise APIError('register:failed', item, item + 'is already in use.')

# 用户注册的信息发送给数据库
@post('/api/users')
async def api_register_user(*, email, name, passwd):
    # 源代码检测名字为空，或者email格式为空，显然没意义。
    # ——REEmail是正则用来判断格式的，没必要所以我没写。
    # if not name or not name.strip():
    #     raise APIValueError('name')
    # if not email or not _RE_EMAIL.match(email):
    #     raise APIValueError('email')
    # if not passwd or not _RE_SHA1.match(passwd):
    #     raise APIValueError('passwd')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)

    # 创建一个用户（密码是通过sha1加密保存）
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
    image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())

    # 保存这个用户到数据库用户表
    await user.save()
    logging.info('save user OK')
    # 构建返回信息
    r = web.Response()
    # 添加cookie
    r.set_cookie(COOKIE_NAME, user2cookie(
        user, 86400), max_age=86400, httponly=True)
    # 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
    user.passwd = '******'
    # 返回的是json数据，所以设置content-type为json的
    r.content_type = 'application/json'
    # 把对象转换成json格式返回
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')


    return r
