#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/11/4

# config_default 默认配置

configs = {
    'db': {  # 定义数据库相关信息
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "password",
        "database": "awesome"
    },
    'session': {
        # 定义会话cookie密钥
        'secret': 'awesome'
    }
}