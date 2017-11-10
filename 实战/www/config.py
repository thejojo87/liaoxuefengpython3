#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/11/4

import config_default





# 自定义字典
class Dict(dict):

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        # 建立键值对关系
        # 这里的names和values是list，zip就是能把这个合并成一个dict
        # 然后按照两个list合并成[(arg1[0],arg2[0],arg3[0]...),(arg1[1],arg2[1],arg3[1]...),,,]
        for k, v in zip(names, values):
            self[k] = v

    # 定义描述符,方便通过点标记法取值,即a.b
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    # 定义描述符,方便通过点标记法设值,即a.b=c
    def __setattr__(self, key, value):
        self[key] = value


# 用override覆盖掉default
def merge(default, override):
    r = {}
    for k,v in default.items():
        # kv在override里存在，需要合并
        if k in override:
            # isinstance是用来判断v是否是dict类型的
            # 这里拿来default的v拿来做判断，
            # 因为default和override字段形式都是一样的。
            # 所以这里的v不是字典，那么就是值，相应的override的v
            # 也是值
            # 如果v是字典，那么应该再递归一次。
            if isinstance(v, dict):
                # 如果v是dict类型的
                r[k] = merge(v, override[k])
            # default的v不是字典，那么就是值，就直接存储override的v
            else:
                r[k] = override[k]
        # 意味着这个kv是default独有的，就直接赋值
        else:
            r[k] = v
    return r

# 将内建字典转换成自定义字典类型
def toDict(d):
    D = Dict()
    for k, v in d.items():
        # 字典某项value仍是字典的,则将value的字典也转换成自定义字典类型
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = toDict(configs)
