#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by thejojo at 2017/10/30

# day3-orm

import aiomysql
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO)


# 打印函数，封装后只需要一个括号就行了
def log(sql, args=()):
    logging.info('SQL:%s ARGS:%s' % (sql, args))


# 创建数据库连接池，避免频繁打开或关闭数据库连接
async def create_pool(loop, **kw):
    logging.info('start creating database connection pool')
    global __pool
    # 调用一个子协程来创建全局连接池，create_pool返回一个pool实例对象
    __pool = await aiomysql.create_pool(
        # 连接的基本属性设置
        host=kw.get('host', 'localhost'),  # 数据库服务器位置，默认本地
        port=kw.get('port', 3306),  # 端口
        user=kw['root'],  # 用户名
        password=kw['password'],  # 密码
        db=kw['db'],  # 数据库名
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),  # 是否自动提交， 默认True

        # 下面是可选项设置
        maxsize=kw.get('maxsize', 10),  # 最大连接池大小，默认10
        minsize=kw.get('minsize', 1),  # 最小
        loop=loop  # 设置消息循环
    )


# 关闭连接池，其实可以不要这个，放在execute里，这里我只是试试而已
async def destroy_pool():
    # 这里并不是声明一个新的pool变量，如果已经存在，那么指向同一个pool，如果不存在那么就为undefined
    global __pool
    try:
        # 表明存在了pool，可以进行销毁了
        if __pool is not None:
            __pool.close()
            await __pool.wait_closed()
    except:
        # 表明nameError发生了，也就是pool变量不存在
        print('pool为空，先去创建pool才能销毁')


# select
async def select(sql, args=None, size=None):
    # sql:sql语句
    # args:填入sql的参数,list类型，如['20111101','xue']
    # size:取多少行记录
    log(sql, args)
    global __pool
    # with...as...的作用就是try...exception...
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned:%s' % len(rs))
        return rs


# execute- 封装INSERT, UPDATE, DELETE
# 语句操作参数一样，所以定义一个通用的执行函数
# 返回操作影响的行号
async def execute(sql, args, autocommit=True):
    log(sql)
    # 这里不用global __pool能直接用？
    global __pool
    async with __pool.get() as conn:
        if not autocommit:
            # 我没看懂，上面select没有这回事啊
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
                print('affected:', affected)
            if not autocommit:
                await conn.commit()
        # 这个函数是个生成器，如果想拿到返回值，必须捕获错误。
        except BaseException as e:
            if not autocommit:
                await conn.rollback()


# 该方法用来将其占位符拼接起来成'?,?,?'的形式，num表示为参数的个数
def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')

    # 以','为分隔符，将列表合成字符串
    return (','.join(L))


# 定义Field类，负责保存数据库表的字段名和字段类型
class Field(object):
    # 表的字段包括，名字，类型，是否为主键和默认值
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        # 返回表名字 字段名 和字段类型
        return "<%s, %s, %s>" % (self.__class__.__name__, self.name, self.column_type)


# 下面是5个存储类型
# 字符串域，映射varchar
# 默认为字段nameNone
class StringField(Field):
    # ddl是什么鬼，貌似是column_type和数据库mysql对应
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


# 布尔类型更不可能做主键了
class BoolField(Field):
    def __init__(self, name=None, default=None):
        super(BoolField, self).__init__(name, 'boolean', False, default)


# 整形
class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super(IntegerField, self).__init__(name, 'int', primary_key, default)


# float
class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super(FloatField, self).__init__(name, 'float', primary_key, default)


# text
class TextField(Field):
    def __init__(self, name=None, default=None):
        super(TextField, self).__init__(name, 'text', False, default)


# metaclass
class ModelMetaclass(type):
    # __new__ 一定要实现
    # 四个参数是第一个参数是将创建的类，之后的参数即是三大永恒命题：
    # 我是谁，我从哪里来，我将到哪里去。 它返回的对象也是三大永恒命题
    # cls:代表要__init__的类，此参数在实例化时由Python解释器自动提供(例如下文的User和Model)
    # bases:代表继承父类的集合
    # attrs:类的方法集合
    def __new__(cls, name, bases, attrs):
        # 第一步要排除Model，因为model是要用的，不能让改掉了。
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # or前面就是说，从字典里获取table字段，attrs是字典，也就是字典的
        # get用法，后面的None就是默认值
        # 如果table没设置，那么就是None或者name。
        # 如果table设置了，那么就是or是左右进行，也就是tablename
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        # 获取Field主键名
        mappings = dict()  # 保存映射关系
        fields = []  # 保存主键以外的属性
        primaryKey = None  # 保存主键

        # k表示字段名，v是定义域。如name=StringField(ddl="varchar50"),k=name,v=StringField(ddl="varchar50")
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                # 这里k是name，id，email等字段
                # v是StringField等Field类，有着name，column，primarykey，default四个属性
                if v.primary_key:
                    # 主键已存在，报错，不可能俩主键
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        # 没找到主键就报错
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        # 这里的目的是去掉类属性，比如u.name
        # 因为类属性通过attrs[k]已经保存了。
        # 当实例被赋值的时候name='test'.这个时候test值是保存在
        # u.['name']里，而u.name 依然没变。
        # 在其他方法里这个会冲突，所以删掉了。
        # 删掉后不能直接用getattr(self, 'name', None)找到u.name
        # 所以会调用getattr(self, 'name')，返回self['name']
        for k in mappings.keys():
            attrs.pop(k)

        # 下面就是要保存的东西了，记录了映射之后，
        # 根据字段名称不同，动态创建了自己
        # 这里attrs返回的数据，子类用self，都能拿到

        # 把所有fields数组里的元素加成'' 变成队列
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        # 保存属性和列的映射关系
        attrs['__mappings__'] = mappings
        # 保存表名
        attrs['__table__'] = tableName
        # 保存主键名称
        attrs['__primary_key__'] = primaryKey
        # 保存主键外的属性名
        attrs['__fields__'] = fields
        # 构造默认的增删改查 语句
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        # attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (
            tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
            tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


# 所有orm映射的基类
# 继承dict是因为要在下面用self[key]来访问**kw属性值
class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super().__init__(**kw)

    # 增加__getattr__方法，使获取属性更加简单，即可通过"a.b"的形式
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    # 增加__setattr__方法，使设置属性更方便，可通过"a.b=c"的形式
    def __setattr__(self, key, value):
        self[key] = value

    # 封装取值方法，通过键取值，不存在返回None
    def getValue(self, key):
        # 这里的getattr 是默认的内置函数
        return getattr(self, key, None)

    # 通过键取值,若值不存在,则返回默认值
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            # 这里mapping是metaclass继承来的，field是定义的。比如FloatField
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                # 通过default取到值之后再将其作为当前值
                setattr(self, key, value)
        return value

    # 对于查询相关的操作，我们都定义为类方法，就可以方便查询，而不必先创建实例再查询
    #
    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        sql = [cls.__select__]
        # cls表示当前类或类的对象可调用该方法，where表示sql中的where，args记录下所有的需要用占位符'?'的参数
        # **kw是一个tuple，里面有多个dict键值对，如{'name',Mary} 多为筛选条件
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):  # 如果是一个整型数，直接在sql语句的limit字段后添加占位符'?'
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:  # limit 有两个参数
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))  # %s输出只能是str类型
        # ''.join(list/tuple/dict)   "|".join(['a','b','c']) -> 'a|b|c'
        rs = await select(' '.join(sql), args)  # 转list为str.
        return [cls(**r) for r in rs]  # cls(**r)调用本类的__init__(方法)

    # 查找某列
    @classmethod
    @asyncio.coroutine
    def findNumber(cls, selectField, where=None, args=None):
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = yield from select(''.join(sql), args, 1)  # Q: 1是什么意思？size=1?为什么按列查找指取1个？
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    # 按主键查找
    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        # **kw表示关键字参数
        # 注意,我们在select函数中,打开的是DictCursor,它会以dict的形式返回结果
        return cls(**rs[0])

    # 插入
    @asyncio.coroutine
    def save(self):
        # 我们在定义__insert__时,将主键放在了末尾.因为属性与值要一一对应,因此通过append的方式将主键加在最后
        # 使用getValueOrDefault方法,可以调用time.time这样的函数来获取值
        print("进入save")
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        print('返回行数：', rows)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    # 更新
    @asyncio.coroutine
    def update(self):
        # 像time.time,next_id之类的函数在插入的时候已经调用过了,没有其他需要实时更新的值,因此调用getValue
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = yield from execute(self.__update__, args)
        print('更新成功！')
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    # 删除
    @asyncio.coroutine
    def remove(self):
        args = [self.getValue(self.__primary_key__)]  # 取得主键作为参数
        rows = yield from execute(self.__delete__, args)
        print('删除成功！')
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)


# 这是测试代码
if __name__ == "__main__":

    class User(Model):
        id = IntegerField('id', primary_key=True)
        name = StringField('username')
        email = StringField('267@qq.com')
        password = StringField('password')


    async def test():
        # 这就是连接代码，生成pool就会自动连接，但是首先要生成数据库才行
        await create_pool(loop=loop, host='localhost', port=3306,
                          root='root', password='password', db='test1')
        print('test')
        user = User(id=8, name='sly', email='slysly759@gmail.com', password='fuckblog')
        await user.save()
        r = await User.find('11')
        print(r)
        r = await User.find_all()
        print(1, r)
        r = await User.find_all(id='12')
        print(2, r)
        await destroy_pool()


    # 获取EventLoop队列：
    loop = asyncio.get_event_loop()
    # 执行协程队列：把这个队列扔进去，因为init需要这个loop
    loop.run_until_complete(test())
    loop.close()
    if loop.is_closed():
        sys.exit(0)
        # loop.run_forever()
