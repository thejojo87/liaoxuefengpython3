#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/11/2

# Day5-编写web框架
import functools
import inspect

# 利用工厂模式，生成GET POST 等方法请求装饰器
from aiohttp import web
# from errors import APIError
from urllib import parse
import logging
from apis import APIError
import asyncio

import os  # rfind


def request(path, *, method):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = method
        wrapper.__route__ = path
        return wrapper

    return decorator


# 下面这个用的是廖雪峰讲过的偏函数 指定传入一个参数为固定值。

get = functools.partial(request, method='GET')
post = functools.partial(request, method='POST')
put = functools.partial(request, method='PUT')
delete = functools.partial(request, method='DELETE')


# ---------------------------- 使用inspect模块中的signature方法来获取函数的参数，实现一些复用功能--
# 关于inspect.Parameter 的  kind 类型有5种：
# POSITIONAL_ONLY		只能是位置参数
# POSITIONAL_OR_KEYWORD	可以是位置参数也可以是关键字参数
# VAR_POSITIONAL			相当于是 *args
# KEYWORD_ONLY			关键字参数且提供了key，相当于是 *,key
# VAR_KEYWORD			相当于是 **kw



def get_required_kw_args(fn):
    # 如果url处理函数需要传入关键字参数，且默认是空得话，获取这个key
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        # param.default == inspect.Parameter.empty这一句表示参数的默认值要为空
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    # 如果url处理函数需要传入关键字参数，获取这个key
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):  # 判断是否有指定命名关键字参数
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_arg(fn):  # 判断是否有关键字参数，VAR_KEYWORD对应**kw
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


# 判断是否存在一个参数叫做request，并且该参数要在其他普通的位置参数之后，即属于*kw或者**kw或者*或者*args之后的参数
def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        # 只能是位置参数POSITIONAL_ONLY
        if found and (
                            param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (
                fn.__name__, str(sig)))
    return found


# RequestHandler目的就是从URL函数中分析其需要接收的参数，从request中获取必要的参数，
# 调用URL函数，然后把结果转换为web.Response对象，这样，就完全符合aiohttp框架的要求：

class RequestHandler(object):  # 初始化一个请求处理类

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    # __call__方法的代码逻辑
    # 1.kw用来保存参数
    # 2.判断request对象是否存在参数，如果存在的话分为post和get
    # 3.如果kw为空，那么把match_info里的资源映射表赋值给kw
    # 4.如果不为空，那么把命名关键字参数赋值给kw
    # 5.完善has_request_arg和_required_kw_args属性
    async def __call__(self, request):
        kw = None
        # 确保有参数  关键字就是kw的key
        # 确保有关键字，确保有需要的关键字，确保有关键字参数而且默认为0
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            # request.method分为post和get
            if request.method == 'POST':
                # 先判断是否存在content_type(媒体格式类型)，一般
                # text/html;charset:utf-8
                if not request.content_type.lower():
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()  # 如果请求json数据格式
                    # 是否参数是dict格式，不是的话提示JSON BODY出错
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params  # 正确的话把request的参数信息给kw
                # POST提交请求的类型
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()  # 调用post方法，注意此处已经使用了装饰器
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':  # get方法比较简单，直接后面跟了string来请求服务器上的资源
                qs = request.query_string
                if qs:
                    kw = dict()
                    # 该方法解析url中?后面的键值对内容保存到kw
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:  # 参数为空说明没有从Request对象中获取到必要参数

            # Resource may have variable path also. For instance, a resource
            # with the path '/a/{name}/c' would match all incoming requests
            # with paths such as '/a/b/c', '/a/1/c', and '/a/etc/c'.


            # A variable part is specified in the form {identifier}, where the
            # identifier can be used later in a request handler to access the
            # matched value for that part. This is done by looking up the
            # identifier in the Request.match_info mapping:
            kw = dict(**request.match_info)
            # 此时kw指向match_info属性，一个变量标识符的名字的dict列表。Request中获取的命名关键字参数必须要在这个dict当中
            # kw不为空时，还要判断下是可变参数还是命名关键字参数，如果是命名关键字参数，则需要remove all unamed kw，这是为啥？
        else:
            # 如果从Request对象中获取到参数了
            # 当没有可变参数，有命名关键字参数时候，kw指向命名关键字参数的内容
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw: 删除所有没有命名的关键字参数
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg: 检查命名关键字参数的名字是否和match_info中的重复
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning(
                        'Duplicate arg name in named arg and kw args: %s' % k)  # 命名参数和关键字参数有名字重复
                kw[k] = v
                # 如果有request这个参数，则把request对象加入kw['request']
        if self._has_request_arg:
            kw['request'] = request
            # check required kw: 检查是否有必要关键字参数
        if self._required_kw_args:
            for name in self._required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_route(app, fn):
    # add_route函数，用来注册一个URL处理函数
    # 获取'__method__'和'__route__'属性，如果有空则抛出异常
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    # 判断fn是不是协程(即@asyncio.coroutine修饰的) 并且 判断是不是fn 是不是一个生成器(generator function)
    if not asyncio.iscoroutine(fn) and not inspect.isgeneratorfunction(fn):
        # 都不是的话，强行修饰为协程
        fn = asyncio.coroutine(fn)
    logging.info('处理add route函数: %s %s => %s (%s)' % (
        method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    # 正式注册为相应的url处理方法
    # 处理方法为RequestHandler的自省函数 '__call__'
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    # 自动搜索传入的module的处理函数
    # 检查传入的module_name是否有.
    # python rfind()返回字符串最后一次出现的位置，如果没有匹配项则返回-1
    n = module_name.rfind('.')
    logging.info('处理add_routes函数：n = %s', n)
    # 没有'.',则传入的是module名
    # __import__方法使用说明请看：http://kaimingwan.com/post/python/python-de-nei-zhi-han-shu-__import__
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
        logging.info('globals = %s', globals()['__name__'])
    else:
        # name = module_name[n+1:]
        # mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
        # 上面两行是廖大大的源代码，但是把传入参数module_name的值改为'handlers.py'的话走这里是报错的，所以改成了下面这样
        mod = __import__(module_name[:n], globals(), locals())
    # mod就是一个模块比如，aaa.bbb mod就是aaa
    # 遍历mod的方法和属性,主要是招处理方法
    # 由于我们定义的处理方法，被@get或@post修饰过，所以方法里会有'__method__'和'__route__'属性
    for attr in dir(mod):
        # 如果是以'_'开头的，一律pass，我们定义的处理方法不是以'_'开头的
        if attr.startswith('_'):
            continue
        # 获取到非'_'开头的属性或方法
        fn = getattr(mod, attr)
        # 取能调用的，说明是方法
        if callable(fn):
            # 检测'__method__'和'__route__'属性
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                # 如果都有，说明使我们定义的处理方法，加到app对象里处理route中
                add_route(app, fn)

# 添加静态页面的路径
def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)   # app是aiohttp库里面的对象，通过router.add_router方法可以指定处理函数。本节代码自己实现了add_router。关于更多请查看aiohttp的库文档：http://aiohttp.readthedocs.org/en/stable/web.html
    logging.info('add static %s => %s' % ('/static/', path))
