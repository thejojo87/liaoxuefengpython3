"# liaoxuefengpython3" 

[github地址](https://github.com/thejojo87/liaoxuefengpython3)

## 参考资料

[从一个大神复制过来](https://github.com/thejojo87/mblog)
[有人参考上面的又写了一遍](https://github.com/songluyi/FuckBlog/blob/9feb9c0ec03ed6247457fcddc302a872a56a5d59/FuckBlog/www/base.py)
[流程总结](https://hk4fun.github.io/2017/10/09/%E5%BB%96%E9%9B%AA%E5%B3%B0web%E5%AE%9E%E6%88%98%E6%80%BB%E7%BB%93/)
[最详细的github](https://github.com/Hk4Fun/awesome-python3-webapp/blob/master/www/config.py)

## Day 1 -  搭建开发环境

### python版本

我用的是3.7
教程是3.5

### 第三方工具

以前用mac的时候pip3直接就好了。
现在真麻烦。
windows里，我用pycharm。
所以先进入项目的setting的编译器设置
![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171029/010402643.png)

安装了异步框架aiohttp和前端模板引擎jinja2，MySQL的Python异步驱动程序aiomysql

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171029/010638239.png)

### mysql

[下载地址](https://dev.mysql.com/downloads/file/?id=473309)


安装完毕后，请务必牢记root口令。为避免遗忘口令，建议直接把root口令设置为password

用户名是root ，密码是password

如何启动？
反正安装后启动后，我用pycharm的数据库，连接成功了


### 项目结构

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171029/010856425.png)


## Day 2 - 编写Web App骨架

新建一个app.py
代码和网页上的不一样。
以代码为准。

就两个函数，一个index函数，一个init函数。

还有三行脚本。
实际就是一个event loop
这里有[异步IO-asyncio的教程](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432090954004980bd351f2cd4cc18c9e6c06d855c498000)

coroutine就是协程
原理就是，从一个函数，用关键字asyncio设置为协程。
然后把这个扔到一个EventLoop里执行。

协程也是一种对象。协程不能直接运行，需要把协程加入到事件循环（loop），由后者在适当的时候调用协程。asyncio.get_event_loop方法可以创建一个事件循环，然后使用run_until_complete将协程注册到事件循环，并启动事件循环。


asyncio是Python 3.4版本引入的标准库，直接内置了对异步IO的支持。

asyncio的编程模型就是一个消息循环。我们从asyncio模块中直接获取一个EventLoop的引用，然后把需要执行的协程扔到EventLoop中执行，就实现了异步IO。

设置为协程貌似两种都可以。
要么在def前面加一个 async 后面加await
要么在上面装饰器声明 @asyncio.coroutine 后面加 yield from

请注意，async和await是针对coroutine的新语法，要使用新的语法，只需要做两步简单的替换：

    把@asyncio.coroutine替换为async；
    把yield from替换为await。

- 遇到了一个大坑。
python3.70的版本和aiohttp有冲突。
引用就syntaxerror错误。
换成3.6完美解决。

流程如下：
生成loop 循环池。
然后把loop丢进init函数。
init函数只进行一次，初始化aiohttp设置为app。
app绑定了index函数和路由。
然后利用app 生成一个 生成器，generator。就是srv
srv只生产了一次，设置为handle，特定网址。

init函数把生成器srv给返回去。
然后run——forever负责一直在监听。

每当产生一个网络请求的时候，srv负责接听。
srv生成一个协程。
如果网址对，那么负责启动一个index函数响应。

用到的知识点有aiohttp，async/await

logging以后再说吧。


## Day 3 - 编写ORM

ORM是什么呢？
对象关系映射（Object Relational Mapping，简称ORM）是一种为了解决面向对象与关系数据库存在的互不匹配的现象的技术。
数据库写起来很麻烦。sql语句。
我们希望能用面向对象的方式创建，删除，插入等操作。
所以需要一个中间件，来替我们把数据类方式转换成数据库语句来插入。

即将一个数据库表映射成一个类，简单说就是将与数据库的多种交互操作，封装成一个类，类里面包含之前的增删查改等操作方法。

为了处理大量用户的请求，采用协程（只有一个线程，控制协程的切换）
，协程是异步的，所以不能采用一般的IO处理（速度太慢，严重影响协程），故采用面向mysql的异步Io：aiomysql。
一次用异步的话，下面都要用异步。

用了一个aiomysql来连接数据库

[aiomysql文档](http://aiomysql.readthedocs.io/en/latest/connection.html)

### 1.创建数据库连接池

我们需要创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。

连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务：

假设用户2又新申请了一个访问。
那么系统应该分出一个协程给他，然后从数据库读取数据返回。
这时候如果连接池存在的话，直接就获取，不需要再连接数据库了吧。

**kw是关键字参数。表示可以只传入必选参数。

这里的pool是global，并且双下划线开头。
这就变成了私有变量，只有内部可以访问，外部不可以。
这不是矛盾吗？一方面create——pool设置为私有变量，另一方面pool又是global。
pool只用一个下划线会如何？
看了说明还是没懂在这里用双下划线开头命名pool什么意思，不是应该不该用下划线吗？
[下划线的说明](https://www.zhihu.com/question/19754941)

这里pool生成函数并没有return任何东西。
按道理返回结果是None，但是pool是global变量。
所以变相赋值结束了。

global用法？ 我看到create和删除都用了global ————pool
那么如果已经存在的话，第二次在别的函数声明后使用是否指向第一个变量？
如果pool变量声明但是没有赋值的话，如果print会出现NameError: name poolis not defined
也就是如果没有create直接destroy那么if __pool is not None:就出错。
name '__pool' is not defined
所以要用try：except来先判断


如果pool声明了，那么？
那么create里声明了一个global的pool，然后在destroy函数里
global pool 指的就是同一个pool
可以进行判断了



kw.get('port', 3306)这是默认值？
d = kwargs.get('d', d_default_value)＃如果未给出该值则d值为d_default_value
复习kw ar 可以看[这个文章](http://kodango.com/variable-arguments-in-python)

既然有创建池，那么应该有销毁吧。
我发现廖雪峰是在excute阶段进行了销毁，估计是为了保险。
但其实应该能分离的。
我就试试分离吧。

pool创建和关闭看aiomysql的api就可以了
[pool的api](http://aiomysql.readthedocs.io/en/latest/pool.html)

下一个封装select
select [语句说明看这里](http://www.runoob.com/mysql/mysql-select-query.html)
为什么要单独封装select呢？其他insert delete，update呢？

>单独封装select，其他insert,update,delete一并封装，理由如下：
使用Cursor对象执行insert，update，delete语句时，执行结果由rowcount返回影响的行数，就可以拿到执行结果。
使用Cursor对象执行select语句时，通过featchall()可以拿到结果集。结果集是一个list，每个元素都是一个tuple，对应一行记录。

### 2.select和execute

这两句是实际执行的mysql语句+数据库连接语句。
用aiomysql的api执行。
[api在这里](http://aiomysql.readthedocs.io/en/latest/cursors.html?highlight=DictCursor)

先拿字典coon，然后拿con的指针cursor，然后cursor用来execute（sql语句）。
最后用cursor.fetchmany来获取结果。

-这里先封装了一个log函数。
封装前要写这个logging.info('SQL:%s :%s' %(sql, args))
封装后就只要log(sql,args) 就行了

函数里几乎每一个操作都有yield from 
这到底是什么呢？

先看看到底都有哪一步。
第一步： pool as conn
第二步： conn.cursor设置为cur
第三步： 进行cur的execute
第四步： 按照size参数，返回指定结果

这是不是都是同步？哪一步是异步？
yield from 到底是什么？
async 和await到底是什么？
是一对一对应吗？本质到底是什么呢？

[async详细教程](https://github.com/ictar/python-doc/blob/master/Python%20Common/Python%20async-await%E6%95%99%E7%A8%8B.md)
本质就是协程。

async 和@asyncio.coroutine 
返回的是一个协程对象，并不运行，和js的promise差太远了。
这个会放进去event循环里，然后稍后执行。

而yieldfrom 和await就是实际调用一个协程。
而yield from必须在@asyncio.coroutine 装饰的函数内使用。

更新更简洁的语法是使用async/await关键字。

并不是一对一对应，而是在async声明的函数内，才能实际调用await

那么回过头看一下上面4个步骤。
第一步 声明为async 意味着，这次select会占用一个协程。
分了一个池子
第二步是按照aiosql的账号链接了个指针，所以需要再分一个。
因为如果不同用户，是需要另外的吧。
第三和第四是执行。

__pool.get() 这个是字典的get方法。
sql.replace('?', '%s'), args or ()
SQL语句的占位符是?，而MySQL的占位符是%s，select()函数在内部自动替换。
后面加  ,args or ()是什么意思呢？
按道理execute里面就该是完整的sql语句。
这里，sql，然后逗号？
貌似是aiomysql的execute里的api
Parameters:	

    query (str) – sql statement
    args (list) – tuple or list of arguments for sql query

然后后面or ()意思是，args如果为0，那么就是args=None处理

--- 
下一步就是execute函数-封装了insert，delete和update

这里第一个不同，参数有一个是autocommit，默认为true
这里加个判断，如果为否，那么就开始一个begin
说真的，没看懂。
我记得数据库里，修改之后还需要commit才会保存修改。
上面select只是查询，并不需要commit
所以先判断autocommit是否为true，
如果是false，那么conn.begin,然后下面进行操作，保存影响的数据。
然后commit
如果是true，那么直接进行操作，不需要commit。
如果出错了，如果是false，那么就指针回滚。因为没有提交。
如果是true，那么raise，我就不知道了。
为什么出错的方式要这么写呢？
因为这个函数有着yield，也就是await，这个函数就是个生成器。
如果想拿到结果，就要捕获错误。
可以看一下[这里](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014317799226173f45ce40636141b6abc8424e12b5fb27000)
有点类似。


### 3.Model
首先思考如何使用orm。
首先model是什么？用来干什么的？
比如说我们要定义一个user对象，那么就要从orm的Model继承。
model这个基础类封装了很多属性，

```python
# 创建实例:
user = User(id=123, name='Michael')
# 存入数据库:
user.insert()
# 查询所有User对象:
users = User.findAll()

>>> user['id']
123
>>> user.id
123

```

首先Model继承于dict，metaclass是ModelMetaclass这个下一步搞定。

model为什么继承于dict呢？
是为了存储属性吗？
[看这里](https://syjs10.github.io/2017/05/23/Python%E4%B8%ADclass%E7%BB%A7%E6%89%BFdict%E4%B9%8B%E5%90%8E%E7%9A%84%E5%8F%98%E5%8C%96/)

继承dict的话，self可以用字典的方式访问**Kw里的内容。


#### 1. init
是init（self, **kw）

```python
def __init__(self, **kw):
        super(Model, self).__init__(**kw)
```

**kw是关键字参数，存储key value对。
这里super(Model, self).__init__(**kw)

super继承父类需要看这个。
[Python中多继承与super()用法](http://www.jackyshen.com/2015/08/19/multi-inheritance-with-super-in-Python/)

python3里可以直接用super().xxx 代替 super(Class, self).xxx
所以这句话意思已经很清楚了。

```python
class User(Model):

user = User(id=123, name='Michael')
```

也就是说，User继承了Model类，
第二句里，user给Model的init函数发送了id和name的字典。
这两个就是**kw了。然后这个会发送的dict和metaclass的init

#### 2  -  __getattr__

```python
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
```

getattr 是，python想要访问不存在的类的方法或者属性的时候，就会调用这个。
。这个可以用于捕捉错误的拼写并且给出指引，使用废弃属性时给出警告（如果你愿意，仍然可以计算并且返回该属性），以及灵活地处理AttributeError。只有当试图访问不存在的属性时它才会被调用，所以这不能算是一个真正的封装的办法。
也就是说，如果我试图访问Model的不存在的属性的时候，因为继承了dict
getattr试图返回init里**kw里的字典值。
如果没找到，那么就报错。

而且还有个好处，可以使得获取属性很简单。
可通过"a.b"的形式

这里有个很好玩的例子

```python
class Chain(object):

    def __init__(self, path=''):
        self._path = path

    def __getattr__(self, path):
        return Chain('%s/%s' % (self._path, path))

    def __str__(self):
        return self._path

    __repr__ = __str__

print(Chain().status.user.timeline.list)

'/status/user/timeline/list'

```

Chain().__getattr__('status').__getattr__('user').__getattr__('timeline').__getattr__('list')


#### 3- __setattr__

这个应该是用来更新属性值的。
有个问题，如果一个属性不存在，那么是不是先调用getter，说找不到呢？

赋值不是用的这个对吧？

```python
    # 增加__setattr__方法,使设置属性更方便,可通过"a.b=c"的形式
    def __setattr__(self, key, value):
        self[key] = value
```

#### 4- getattr和getValueOrDefault

这里没什么好说的，只是，这里的getattr是默认的内置函数，和上面那个不一样。

第二个如果键值不存在，那么应该返回默认值。

```python
field = self.__mappings__[key] # field是一个定义域!比如FloatField
```

这个应该是metaclass里的mappings继承的。

```python
value = field.default() if callable(field.default) else field.default
```

三目运算语法: if_rt if condition else else_rt

基本含义: 如果condition条件为True则返回if_rt值否则执行else_rt值

如果 field 的 default 是个方法， value 就是 default() 被调用后返回的值，
如果不是， value 就是 default 本身。
这里是字段的默认值可能是个值，也可能是个函数，
如果默认值是个值，就取这个值，如果是个函数，就调用它，去调用后返回的结果。

id的StringField.default=next_id,因此调用该函数生成独立id。实现自增
FloatFiled.default=time.time数,因此调用time.time函数返回当前时间。当前时间做id

普通属性的StringField默认为None,因此还是返回None


### 4. field

这里要存储各种字段，比如说字符串，比如说数字什么的。
当然这里也有个父类。
为什么放在orm里呢？
单独放在其他地方是不是也可以呢？
但是想想，设置User的时候，从orm import Model，确实也还要stringfield
放在这里也好。

#### 1. 父类Field
没什么好说的，继承于object
有init方法，包括，名字，类型，是否为主键和默认值

还有个__str__方法

__str__的目的是为print 这样的打印函数调用而设计的，当print 一个对象时，会自动调用其__str__方法

```python
class test(object):

    def __init__(self, test = 0):
        self.test = 3

    def __str__(self):
        return "asdfklasd == %s" % self.test

a = test(10)
print(a)
```

这里column_type 我看到stringfield里是ddl
貌似ddl是mysql里的语句称号。
StringField是ddl语句？


### 5. metaclass 
什么时候有用呢？
爬虫的时候，orm的时候。
modelmetaclass到底做了什么作用？

每次初始化一个User实例的时候的参数都是不一样的。
这意味着数据库表都是不一样的。
两个User意味着两张表。
用字典的方式传给Model属性。
Model里的方法都是使用的方法，比如find方法。
按照key来找数据库里的数据。
那么字典里的数据必须要有一个抽出，并且放在mapping属性的动作。
Model只负责从mapping里抽出来就可以了。
这里的metaclass就做了扫描映射关系，并存储到自身的类属性中__table__、__mappings__等。

ModelMetaclass的工作主要是为一个数据库表映射成一个封装的类做准备：
读取具体子类(user)的映射信息
创造类的时候，排除对Model类的修改
在当前类中查找所有的类属性(attrs)，如果找到Field属性，就将其保存到__mappings__的dict中，同时从类属性中删除Field(防止实例属性遮住类的同名属性)
将数据库表名保存到__table__中


这里有个问题：
> 元类的作用和继承有什么区别？
How are Python metaclasses different from regular class inheritance? [duplicate]

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171101/045952903.png)


比较有用的教程-
[教程一](http://python.jobbole.com/88795/)
metaclass 继承自type，
metaclass 必须实现__new__方法，这个在init之前启动
它接受四个参数，第一个参数是将要创建的类。
也就是self类似啦。类init的时候不都是用self操作么。

剩下的就是，我是谁，我从哪里来，我要到哪里去。
我是谁，父类，我的参数都有啥。

```python
if name=='Model':
    return type.__new__(cls, name, bases, attrs)
```

第一步就是排除掉Model类名字。
因为name代表着将要创建的类名，我们是从Model追溯来的，
Model就是基类，如果你print(name)的话，会依次打印出Model,User,Blog。

但是return type.__new__(cls,name,bases,attrs)
意味着没修改？还是确实修改了，但是没动？
应该是根本没修改，就直接动用type生成二了，等于没有做任何下面的映射了吧。
在这里Model(Model)会如何？
生成Model，然后追溯metaclass，然后又生成一个Model，
不是会无线循环吗？
经过实验，并不会无限循环，
但是却会产生一个集成Model的Model类。
但是有没有映射我就不知道了，得需要写完后实验一下。
排除model 是因为要排除对model类的修改
因为Model类主要就是用来被继承的,其不存在与数据库表的映射


```python
class User(Model):
    # 定义类的属性到列的映射：
    id = IntegerField('id')
    name = StringField('username')
    email = StringField('email')
    password = StringField('password')

# 创建一个实例：
u = User(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
```

下面是获取tablename。

```python
        # or前面就是说，从字典里获取table字段，attrs是字典，也就是字典的
        # get用法，后面的None就是默认值
        # 如果table没设置，那么就是None或者name。
        # 如果table设置了，那么就是or是左右进行，也就是tablename
        tableName = attrs.get('__table__', None) or name
```

下面获取Field所有主键名和Field

```python
        # 获取Field主键名
        mappings = dict() # 保存映射关系
        fields=[] # 保存主键以外的属性
        primaryKey=None #保存主键

        # k表示字段名，v是定义域。如name=StringField(ddl="varchar50"),k=name,v=StringField(ddl="varchar50")
        for k,v in attrs.items():
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
```

下面思索了良久。
下一步就是从类属性中删除已经加入了映射字典的键，以免重名。
有没有可能attra有着重名的建？
会不会重复映射？如果有重名的，应该会只录后面那条数据。
等于更新了。
字典能不能重名的key？
字典的key值是不可以重复的，如果重复默认取最后一个value值。

那么为什么要从原来的attra删除，成另一个dict？

大概如下

```python
attrs[k]里面保存的是类属性，按说后面赋值时，会拿实例属性会覆盖掉它，但是...并没有！

类属性(比如name)的引用是 u.name， 有没有？  

Model是dict的子类,有没有？ 

在实例被赋值(name='test'...)、进行init初始化之后，'test'值还是保存在u.['name']中，没有再赋值给u.name， 有没有? 

getValue或者getValueOrDefault时，是直接getattr(self, 'name', None) 有没有？  

结果类属性里面有这个name，所以直接返回表属性的值，结果报错，有没有？ 

而当attrs.pop(k)之后，一切就清静了... 

getattr(self, 'name', None)是不能直接找到u.name的值，

所以调用getattr(self, 'name')方法，

然后你让它返回的是self['name']....
```

```python
        # 这里的目的是去掉类属性，比如u.name
        # 因为类属性通过attrs[k]已经保存了。
        # 当实例被赋值的时候name='test'.这个时候test值是保存在
        # u.['name']里，而u.name 依然没变。
        # 在其他方法里这个会冲突，所以删掉了。
        # 删掉后不能直接用getattr(self, 'name', None)找到u.name
        # 所以会调用getattr(self, 'name')，返回self['name']
```

下一步
```python
escaped_fields = list(map(lambda f: '`%s`' % f, fields))
```

首先使用list() 变成 一个队列
下一层就是map(function, iterable)
iterable就是field 数组
function就是lambda f: '`%s`' % f
匿名函数lambda x: x * x实际上就是：
def f(x):
    return x * x
关键字lambda表示匿名函数，冒号前面的x表示函数参数。
匿名函数有个限制，就是只能有一个表达式，不用写return，返回值就是该表达式的结果。

也就是说，把所有field数组里的元素全部加 ’' 变成一个队列。

下面很简单，保存映射。构造默认的增删改查语句。


### 6. 补完Model里查询相关的各种方法-类方法

添加的各种方法都是类方法。
什么是类方法？

[这里有个文章说明](http://30daydo.com/article/89)

Model要达到的效果如下
因为User是继承于Model，所以Model添加类方法，等于User也可以使用。

```python
user = yield from User.find('123')

user = User(id=123, name='Michael')
yield from user.save()
```

类方法第一行 @classmethod
开始写函数，参数第一个是cls，表示调用当前的类名。
返回的是一个init之后的类。

怎么调用呢？

```python
r=Data_test2.get_date("2016-8-6")
r.out_date()
```
如果不使用类方法。因为类并没有实例化。
所以所以并不会经过init初始化。
init里设置的各种都是无效的，所以当然会出错。
也就是说classmethod返回一个不用实例初始化，然后init的类。
这样做的好处在于，对于查询相关的操作，我们都定义为类方法，就可以方便查询，而不必先创建实例再查询


一共6个类方法- 我跳过去了
#### 1. find——all 方法
这里就是把参数组合成真正的sql语句的地方。
我就跳过去这里了，因为现在还不太懂sql。




### 7. orm如何测试呢？

创建测试代码

```python
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
```


## Day 4 - 编写Model

分为两个部分，
编写model和初始化数据库表

### 编写model

在编写ORM时，给一个Field增加一个default参数可以让ORM自己填入缺省值，非常方便。并且，缺省值可以作为函数对象传入，在调用save()时自动计算。

例如，主键id的缺省值是函数next_id，创建时间created_at的缺省值是函数time.time，可以自动设置当前日期和时间。

日期和时间用float类型存储在数据库中，而不是datetime类型，这么做的好处是不必关心数据库的时区以及时区转换问题，排序非常简单，显示的时候，只需要做一个float到str的转换，也非常容易。

### 初始化数据库表

这里涉及到数据库的操作了。

[数据库语句说明看这里](https://www.liaoxuefeng.com/discuss/001409195742008d822b26cf3de46aea14f2b7378a1ba91000/0014750354404744cfefbf0022a43f285ea03defffdce37000)\

难点在于这一句

```sql
# schema.sql

grant select, insert, update, delete on awesome.* to 'www-data'@'localhost' identified by 'www-data';
```
awesome是什么？是本地数据库名称（db）
第一个www-data为数据库用户名(user),
localhost为主机名(host),
第二个www-data为www-data用户的密码(password)
schema.sql的作用为使用脚本帮你在本地的mysql上自动创建名为awesome的数据库。

```python
# 与上面参数相对应的为：

# orm_test.py(测试orm代码，建议新建*.py文件用于测试，最好不要放在app中)

async def test():
    await orm.create_pool(user='www-data', password='www-data', database='awesome')
```
 
 我先试一下完全不修改按照廖雪峰的来写入。
 
 写入方法就是pycharm里，直接把sql文件拖入localhost就可以了
 
 ![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171101/144714556.png)
 结果是 被拒绝了
 
 ![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171101/144626398.png)
 
 仔细思考，感觉会不会是创建用户池的时候user用了个root，会不会是这个不对？
 
 然后sql语句改成
 
 ```python
 grant select, insert, update, delete on awesome.* to 'root'@'localhost' identified by 'password';
 ```
 
 就成功了
 
 ![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171101/145956156.png)
 多了一个awesome是数据库表
 
 ![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171101/150110491.png)
 
 ![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171101/150127073.png)
 
 pycharm里，点击localhost下面的Schemas，就可以切换表。
 当中选择awesome就可以看到了。
 
 但是当我选择test代码的时候跳出来说，
 pymysql.err.ProgrammingError: (1146, "Table 'awesome.user' doesn't exist")
 确实表里只有users并不是user
 那么我不搜索，不用find，只save可以吗？
 进入save
返回行数： None
WARNING:root:failed to insert record: affected rows: None

问题在于，models文件里，User类里，table名字，我写的是users
但是 这里是INFO:root:found model: User (table: User)

哪里不对呢？

数据库表里是users 表。
这个是mysql语句来生成的。

models里，User类的__table__ 也依然是users

我如果修改这个，感觉什么也没有发生
Info里modelUser里的table 依然是User
而写入操作的时候pymysql.err.ProgrammingError: (1146, "Table 'awesome.user' doesn't exist")

先解决model table User的问题吧。

首先程序新建了一个User类，继承了Model
问题就在这里，我在models.py文件里建造了User类，设置了table
但是我并没有在orm的测试代码里引入，而是直接又新建了一个User类。
所以我决定新建一个测试脚本文件。

### 编写测试脚本文件

第一步就是要引入orm和models
我发现第一步我就遇到了难题

import orm写着 no module named orm
实际用的时候发现其实没问题

当我把www文件夹，mark成source文件夹之后警告就停止了

下一步，我从models文件引入User
ImportError: attempted relative import with no known parent package
原因是我在models文件里，引入orm的函数的时候，使用了相对地址

```python
from .orm import Model, TextField, BoolField, IntegerField, FloatField, StringField
```

而相对地址如果再次被引用就会出错，我把.去掉就没问题了
但是我测试的数据，我试着生成，然后保存。
发现无法插入数据。
运行完全没问题呀。

第一句是进入save
然后是execute，我发现我上面写错了，漏了两行。

之后又出现了新的问题，
"Column 'admin' cannot be null"

admin是bool类型，我并没有设置default。
所以我添加了，然后就输入成功了。


## Day 5 - 编写Web框架

### 思路
[大神的说明文章](http://www.qiangtaoli.com/bootstrap/blog/001466339384240fec2e91483ac41bdb5352c1034be03e9000)

现在写的这个博客是采用MVC框架，也就是 Model-View-Controller （模型-视图-控制器），day5的主要任务是建立View（网页）和Controller（路由）之间的桥梁。具体的方法就是通过request（请求）来达到交互的目的。web框架会把Controller的指令构造成一个request发送给View，然后动态生成前端面页；用户会在前端页面进行某些操作，然后通过request传送回后端，在传回后端之前会经过对request的解析，转变成后端可以处理的事务。day5就是要对这些request进行标准化处理的实现。

aiohttp是一个较底层的框架，当有HTTP请求进入，aiohttp会生成一个request对象，经处理后返回一个Response对象。
但是，中间的处理过程需要我们自行去完成，所以我们要在aiohttp基础上自己封装一个框架。

#### 如果只用aiohttp编写试图函数会如何？
1. 编写一个async/await装饰的函数。进入request
2. 然后从request里获取需要的参数
3. 自行构造返回的Response对象

我们就是要把这个封装起来。
该怎么做呢？
1、通过get/post装饰器、HandlerRequest类来封装视图函数（URL处理函数），让他能正确调用HTTP请求中附带的参数。 
2、通过middlerware处理视图函数返回的参数，构造Response对象以此返回HTTP响应。

### 一共修改了两个文件app.py 和coroweb.py

### coroweb.py文件

#### 1.get装饰器

我们想要达到的效果如下：

```python
处理带参数的URL/blog/{id}可以这么写：

@get('/blog/{id}')
def get_blog(id):
    pass

处理query_string参数可以通过关键字参数**kw或者命名关键字参数接收：

@get('/api/comments')
def api_comments(*, page='1'):
    pass

```

这就是个装饰器，获取的参数是path而不是func

-问题一： path这个参数该怎么使用？

答案： 因为path并不是func，所以需要一层返回decorator的高阶函数。
如果不是因为在这个原因，那么get下面直接是wrapper函数了。
所以为了函数名字正常化，所以使用了@functools.wraps(func)。

wrapper获取path，存在返回的函数的内置参数里。

假设调用这个get装饰器的函数名为now

```python
@get(path)
def now():
    pass
```

这个等于now = get(path)(now)
这里首先执行 get(path) 返回的是decorator函数。
然后再调用decorator(func) 也就是now,
最终返回的是wrapper函数。

说明和案例看[廖雪峰-装饰器](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014318435599930270c0381a3b44db991cd6d858064ac0000)

-问题二：functools.wraps这个偏函数有什么作用？

因为get需要path参数，所以不能直接用func做参数。
所以多加了一层高阶函数，返回wrapper函数。
因此会改变__name__等属性，加了这一句，这些属性会自动更改。

-问题三： method和route这个是私有变量吧？能正常用吗？

再看看吧。

```python
def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator
```

#### 2.post装饰器
和上面get装饰器代码一模一样，除了method 换成了post。
这个非常不科学。

互联网有着get post put 和delete。
如果这么说是不是一模一样的代码写4次？

#### 3.oop的get/post/put/delete装饰器方法-用了偏函数

```python
    # 建立视图函数装饰器，用来存储、附带URL信息  
    def Handler_decorator(path, *, method):  
        def decorator(func):  
            @functools.wraps(func)  
            def warpper(*args, **kw):  
                return func(*args, **kw)          
            warpper.__route__ = path  
            warpper.__method__ = method  
            return warpper  
        return decorator  
    # 偏函数。GET POST 方法的路由装饰器  
    get = functools.partial(Handler_decorator, method = 'GET')  
    post = functools.partial(Handler_decorator, method = 'POST')  
```

不过我看到网友的代码，Handle_decorator直接用了request这个函数名。
没问题吗？有点疑惑。

#### 4.inspect模块，解析视图函数的参数
这是从url获取参数，等用在request参数里

我看到这些重复的太多了吧。
有没有办法能简化？
基本上除了参数和条件，剩下代码都一模一样。
但是这个具体怎么变化呢？
毫无头绪，需要实际案例来分析一下

inspect模块是什么呢？

[inspect教程](http://blog.csdn.net/weixin_35955795/article/details/53053762)

具体怎么使用的呢？

```python
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
```

这里的fn是什么？函数？变量？
get_required_kw_args这个是在RequestHandler函数的init里用的。
RequestHandler函数是在add_route(app, fn)这个函数里使用的。
也就是说，这里的fn就是add_route的fn
而这个又是在add_routes(app, module_name)函数使用的
而这里fn就是fn = getattr(mod, attr) 也就是说遍历mod的方法和属性。
下面只取方法（__name__）之类的
mod是module_name名字截取的。
还是没看懂fn到底是什么样的数据。
应该是函数带着参数块

inspect说明
a函数，带着一些参数。
然后inspect.signature(fn)就变成了参数块如（a, b=0, *c, d, e=1, **f）
然后把这个.paramerters就变成了 orderedDict 字典来储存参数块
name是字典的key，param是字典的值
param.kind就是 上面的5种属性值。

到现在为止知道了 fn是一个参数。

#### 4.参数解析函数们

廖雪峰的源代码有着5个函数。
都是输入fn，获取fn的函数，然后分为好几个类型。
就是重复太多了。
我有两个选择，一个是按照源代码写。
另一个是[重构](https://github.com/songluyi/FuckBlog/blob/9feb9c0ec03ed6247457fcddc302a872a56a5d59/FuckBlog/www/base.py)

一共是5个函数来判断。

1. 有关键字参数，并且默认为空,那么获取这个key
2. 有关键字（感觉1包括在2里了），那么获取这个key
3. 是否有指定的key，相当于 *,key
4. 是否有关键字参数, 相当于**kw
5. 判断是否存在一个参数叫做request，并且该参数要在其他普通的位置参数之后，
即属于*kw或者**kw或者*或者*args之后的参数

廖大的意思是想把URL参数和GET、POST方法得到的参数彻底分离。

    GET、POST方法的参数必需是KEYWORD_ONLY
    URL参数是POSITIONAL_OR_KEYWORD
    REQUEST参数要位于最后一个POSITIONAL_OR_KEYWORD之后的任何地方

[这个讨论蛮有意思](https://www.liaoxuefeng.com/discuss/001409195742008d822b26cf3de46aea14f2b7378a1ba91000/00147377613597389bfa5b0200f49beaca0a9b1947a0565000)

这里最后一个函数有一个continue

```python
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        # 只能是位置参数POSITIONAL_ONLY
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (
                fn.__name__, str(sig)))
return found
```

continue是跳出这次循环的意思。
就是不进行下面的判断，这次直接退出。
然后继续判断下一个参数


#### 5.RequestHandle-本质就是中间件
上面视图函数装饰器只不过是提取了path。
但是我们需要从一个request请求，提取更多参数，
用类来处理并且对视图函数封装。
视图函数指的是URL处理函数。

使用者编写的URL处理函数不一定是一个coroutine，因此我们用RequestHandler()来封装一个URL处理函数。
RequestHandler是一个类，分析视图函数所需的参数，再从request对象中将参数提取，调用视图函数（URL处理函数），并返回web.Response对象。
由于其定义了__call__()方法，其实例对象可以看作函数。
用这样一个RequestHandler类，就能处理各类request向对应视图函数发起的请求了。

- call函数是什么呢？

call就是不用实例的类的()的重载

[说明一](http://blog.csdn.net/networm3/article/details/8645185)
[说明二](http://blog.csdn.net/rubbishcan/article/details/12402341)

为什么用在这里？
wsgi里，wsgi会加载一个app，要接受两个参数。
app可以用函数来定义。
也可以用类中的call方法来定义。

```python
    class App():  
        def __call__(self, environ, start_response):  
            req = Request(environ)  
            resp = Response('Hello world')  
            return resp(environ, start_response)  
```

我还是不太懂什么叫wsgi，为什么用call，有什么好处

[这个教程很强大-wsgi](http://www.oschina.net/news/76907/python-web-basic-of-wsgi)

wsgi是一切django，flask等的基础。
所以一个WSGI应用最重要的部分是什么呢？

    一个WSGI应用是Python可调用的，就像一个函数，一个类，或者一个有__call__方法的类实例

    可调用的应用程序必须接受两个参数：environ，一个包含必要数据的Python字典，start_fn，它自己是可调用的。

    应用程序必须能调用start_fn和两个参数：状态码（字符串），和一个头部以两个元组表述的列表。

    应用程序返回一个在返回体里包含bytes的方便的可迭代对象，流式的部分——例如，一个个只包含“Hello，World！”字符串的列表。（如果app是一个类的话，可以在__iter__方法里完成）
    
    def app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])    
    return ["Hello World!\n"]

call的好处在于，不用实例化。
只要在下面 就可以了。

```python
class Application(object):
    def __call__(self, environ, start_fn):
        start_fn('200 OK', [('Content-Type', 'text/plain')])        
        yield "Hello World!\n"
app = Application()
```

为什么要有RequestHandle函数？

中间件是一种方便扩展WSGI应用功能性的方法。因为你只需提供一个可调用的对象，你可以任意把它包裹在其他函数里。

例如，假设我们想检测一下environ里面的内容。我们可以轻易地创建一个中间件来完成，如下所示：

```python
import pprint
def handler(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])    
    return ["Hello World!\n"]
def log_environ(handler):
    def _inner(environ, start_fn):
        pprint.pprint(environ)        
        return handler(environ, start_fn)    
    return _inner

app = log_environ(handler)
```

再来个路由的例子

```python
routes = {    
    '/': home_handler,    
    '/about': about_handler,
}
class Application(object):
    def __init__(self, routes):
        self.routes = routes
            
    def not_found(self, environ, start_fn):
        start_fn('404 Not Found', [('Content-Type', 'text/plain')])        
        return ['404 Not Found']    
    def __call__(self, environ, start_fn):
        handler = self.routes.get(environ.get('PATH_INFO')) or self.not_found        
        return handler(environ, start_fn)
```

- 第一部分是init
init了app，fn，还有上面5个判断函数。

- 第二部分是call
call接收request参数。
request参数是aiohttp的一个类或者实例。
request会传递给add_route

有点不太明白。
RequestHandler接收app和fn
用fn来判断是否存在**kw里的key什么的。5个判断。
但是RequestHandler的call函数的参数是request。
这两个有什么联系吗？

首先在app.py里，生成一个app对象。
app对象调用response_factory这个中间件。
这里调用了handle，也就是RequestHandler的call函数，这时候call函数就收到了request。



然后把这个发送到coroweb文件的add_routers 和add_static对象里。
这里获得了app和fn

这两条线怎么联系在一起的？

懂了。
使用call的时候一定是首先运行init的。

request参数可以被省略掉。
[看这个解释](https://www.liaoxuefeng.com/discuss/001409195742008d822b26cf3de46aea14f2b7378a1ba91000/001462893855750f848630bb19c43c582fdff90f58cbee0000)

至于为什么能被省略要看官方文档
或者 [这个文档说明](http://www.cnblogs.com/ameile/p/5589808.html)

这里就是说，app.router.add_route('GET', '/', index)
这里的index已经就认定为handle函数了。等于index(request)
所以根本不用传参数，只要index定义的时候写上request就可以用了。

就像day2的时候，index根本没发送request参数。

然后在这里的话，下面的add_route函数是这样写的。

app.router.add_route(method, path, RequestHandler(app, fn))

而RequestHandler(app, fn) 等于 RequestHandler(app, fn)(request)
而最终会在app.py里的response_factory(app, handler)里的r = await handler(request)
调用，等于 RequestHandler(app, fn)(request)
这时候app有了，fn有了，request也有了。

首先进行判断有没有kw 关键字

有关键字的时候判断request的方法是post还是get
post复杂一点，查看字段类型。
get简单直接后面跟了string来请求服务器上的资源。解析后保存到kw

get的时候使用urllib import parse，利用这个来

这后面的逻辑，如果没有实际案例，我觉得很难理解都是判断了什么。
所以我先跳过去了。
我都不知道传进来了什么（传进来的是app，和fn），又传出去了什么。
只知道这个接受request，然后转换格式给服务器。

需要注意的是这里有个APIError，需要调用。
这个得新建一个apis文件，从这里调用。
这个会在Day10讲到。所以这个先跳过去。


#### 6. add_route(app, fn)函数

add_route函数是做什么的？

1. 注册一个URL处理函数-最后一行
2. 验证函数是否有包含URL的响应方法与路径信息
3. 将函数变为协程

这个函数输入什么参数？
app，fn 
fn就是（参数的字典块吧），一个方法，包括参数，包括方法的实现
app应该是aiohttp的实例。

第一行和第二行接收fn里method和route的值，后面是None，
getattr可以放三个参数，第一个参数是obj，第二个是method，第三个是默认值。
这里的method是get或者post字段

```python
getattr(object, name[, default]) -> value

Get a named attribute from an object; getattr(x, 'y') is equivalent to x.y.
When a default argument is given, it is returned when the attribute doesn't
exist; without it, an exception is raised in that case.
```

如果method和route都为空，那么跳出警告。

下面判断fn是不是协程，并且判断是不是一个生成器。
如果不是的话，修饰为协程。

下面是logging
再下面正式注册为RequestHandler的call函数，顺便把app和fn传进去。
用的是aiohttp的api，path和method，然后处理函数。

#### 7. add_routes(app, module_name)函数

这个函数目的是
因为add_route()注册函数会调用很多次，所以想做批量注册。
输入app，和函数所在文件的路径，那么add_routes筛选文件内所有符合注册条件的函数。

首先判断传入的module_name参数里又没有.号
rfind()返回字符串最后一次出现的位置，如果没有匹配项则返回-1
如果没有匹配项目，那么传入的是module名字
如果没有匹配项目，那么使用__import__函数
import函数可以看这里[import函数](http://kaimingwan.com/post/python/python-de-nei-zhi-han-shu-__import__)
这一段涉及到global和locals，涉及到命名空间。
[import函数又一文章](http://python.jobbole.com/87492/)
需要仔细分析。

globals 和locals都是默认值。

但是当n不等于-1的时候，这里把廖雪峰的源代码改了。

我先姑且按照他的方案走，试一下。
最后要自己走一遍流程。

下一步用dir(mod)的方式返回实例属性和构造类以及所有基类的属性列表。

然后获取这个模块的方法，如果存在method和route，那么就用add_route函数注册。

add_route函数设置这个route和handle函数。

什么时候具体调用呢？貌似继续写才能知道。

#### 8.add_static(app)函数

app是aiohttp的实例。
没什么好说的，就是设置app的static文件在哪里找罢了。
获取当前path，然后用api设置。

要在目录里新建一个static文件夹

到这里coroweb.py就完成了。
下一步就是要修改app.py文件了

### app.py文件

#### 1.app.py里jinja2模板和自注册的支持

把这些放到app.py真的合适吗？

jinja2是什么？
就是模板语言，写html的时候可以像Django模板一样能写得简单点。

Environment是核心类。
用这个实例保存配置，对象，文件路径来加载模板。
初始化就是创建这个实例，然后传进参数过去，
然后用get_template()加载模板，
最后用render()方法来渲染模板。

更详细的可以看[这里](http://blog.csdn.net/qq_38801354/article/details/77150637)

没什么可说的就是init jinja2函数，并且初始化了一个datetime_filter
这个应该在Day8

#### 2.编写中间件
中间件是什么？
是aiohttp中的一个拦截器。
首先初始化一个app。
然后app，可以经过中间件，传入add_route函数，用这个来生成路由，这里由RequestHandler函数
来处理，转化成函数。

至于输出的时候，同样，经过middleware处理，转化成web.response对象。

一轮过后，如何将函数返回值转化为web.response对象呢？
这里引入aiohttp框架的web.Application()中的middleware参数。
middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理。一个middleware可以改变URL的输入、输出，甚至可以决定不继续处理而直接返回。middleware的用处就在于把通用的功能从每个URL处理函数中拿出来，集中放到一个地方。
在我看来，middleware的感觉有点像装饰器，这与上面编写的RequestHandler有点类似。
有官方文档可以知道，当创建web.appliction的时候，可以设置middleware参数，而middleware的设置是通过创建一些middleware factory(协程函数)。这些middleware factory接受一个app实例，一个handler两个参数，并返回一个新的handler。

#### 4.记录URL日志的logger作为中间件

```python
async def logger_factory(app,handler):#协程，两个参数
    async def logger_middleware(request):#协程，request作为参数
        logging.info('Request: %s %s'%(request.method,request.path))#日志
        return await handler(request)#返回
    return logger_middleware
```

代码本身没难度，相当简单易懂。
难点在于框架运行逻辑。

这个factory什么时候运行？在哪里被调用？
是自动？还是每次被人用？就是全自动。
handler函数，貌似还没规定。这个一会要怎么传？
下面注册的时候就规定好了。aiohttp的特性。

app.router.add_route('GET', '/index', index)
 
这样一来，我们添加路由的时候，GET，/index，index 
这三个信息最终会被封装成一个 ResourceRoute 类型的对象，然后再经过层层封装，
最终会变成 app 对象内部的一个属性，
你多次调用这个方法添加其他的路由就会有多个 ResourceRoute 对象封装进 app.

logger factory的handle并不是固定的。
每次一个app router 实例化，封装成app对象内部的一个属性的时候，
也就是增加一个router的时候。
logger factory就会赋值，router的handler函数，传进去，又传出来。

什么时候运行？
就是发出一个request请求的时候。
然后发送到handlers.py里的各个相应的url函数进行处理，比如说index函数。
因为这就是注册router的参数。

然后handler函数返回一个response，这个会被RequestHandle先处理（hook），
主要是从url函数中解析需要接收的参数，
进而从request中获取必要的参数构造成字典以**kw传给该url函数并调用。
最后在应答返回数据前会被response_factory所拦截，进行模板的渲染，
将request handler的返回值根据返回的类型转换为web.Response对象，吻合aiohttp框架的需求

[思路看这里](https://hk4fun.github.io/2017/10/09/%E5%BB%96%E9%9B%AA%E5%B3%B0web%E5%AE%9E%E6%88%98%E6%80%BB%E7%BB%93/)
[代码思路看这里](https://github.com/zhouxinkai/awesome-python3-webapp/blob/master/www/app.py)


#### 5.response_factory

对应的响应对象response的处理工序流水线先后依次是:
由handler构造出要返回的具体对象
然后在这个返回的对象上加上'__method__'和'__route__'属性，以标识别这个对象并使接下来的程序容易处理
RequestHandler目的就是从请求对象request的请求content中获取必要的参数，调用URL处理函数,然后把结果返回给response_factory
response_factory在拿到经过处理后的对象，经过一系列类型判断，构造出正确web.Response对象，以正确的方式返回给客户端

#### 6.修改app.py的init函数

就只加了这个
```python
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    # 添加URL处理函数, 参数handlers为模块名
    add_routes(app, 'handlers')
    # 添加CSS等静态文件路径
    add_static(app)
```

这里要注意，handlers是handlers.py这个文件名。并不是函数或者参数，是字符串，文件名。
扫描所有这个文件里的所有handler函数，并且注册



#### 7.新建一个handlers.py

我意识到这里新建了这个文件。
要把index函数因为这是handler函数
和app.router.add_route('GET', '/', index)这句给删掉。
因为已经有了add_routes(app, 'handlers')

该怎么做呢？

```python
from coroweb import get, post
from models import User
import asyncio
from aiohttp import web

@get('/')
async def index(request):
    # users = await User.findAll()
    return web.Response(body=b'<h1>Awesome users</h1>', content_type='text/html', charset='UTF-8')
```

本来我想测试一下数据库存取，发现了一个错误。

File "C:\Users\thejojo\Desktop\coding\python\廖雪峰\实战\www\orm.py", line 64, in select
    async with __pool.get() as conn:
NameError: name '__pool' is not defined
估计是orm出错了吧。

其实就是因为app没有引入orm，没有引入账号。

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171104/142007137.png)


## Day 6 - 编写配置文件

为了编写配置，这里要新建3个文件

### config_default.py

这里是用字典方式储存的。
两个key，db 和session
db存储数据库相关信息
session是 定义会话cookie密钥

### config_override.py

这个不需要重写其他字段，只是把关键字段覆盖掉就可以了。
所以只有一个字典里一个db key和host 字段

### config.py-整合config配置的主文件

这里说到要优先从configoverride里读取。
这里就要写从配置文件读取数据，并且加工整合的主程序。

但是应该给个选项吧？
这个选项在哪里写？
是在app？

### config.py-merge函数

这是用来融合覆盖配置的函数。
新建一个空字典，而不修改任何其他配置
这里采用了一个递归。
因为有可能配置有好几层递归。
但是无论怎么样，最终目的，是
要给r[k]一层层赋值。

如果override里没有k，那么就直接写入。
如果override里有k，那么再查k的v是不是字典。
如果不是字典，那就是说就是值，override[k]直接覆盖r[k]。
如果是字典，那么说明是进一步的字典。
递归参数为v和override[k]

### config.py- toDict函数和Dict类

这是要将内建字典转换成自定义字典类型

判断逻辑和merge函数一模一样，
如果是字典，就继续递归，如果不是那么就经过处理重新保存
主要功能是添加一种取值方式a_dict.key，相当于a_dict['key']，这个功能不是必要的

有点不明白的是zip(names, values)

[需要看这里](https://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python)

这里参数是这样的

```python
keys = ('name', 'age', 'food')
values = ('Monty', 42, 'spam')
# 变成这样
dict = {'name' : 'Monty', 'age' : 42, 'food' : 'spam'}
```

toDict函数本身不改变原来的dict的数据和结构。
但是toDict函数新建了一个Dict类的D变量。
这个Dict类，用了getattr 和setattr 添加了一个a.b = c
的用法。

等于是一个洗点+加了一个功能。

```python
dict转换成Dict后可以这么读取配置：configs.db.host就能读到host的值。
当然configs[db][host]也可以读到

loop.run_until_complete(orm.create_pool(loop, user=configs.db.user, password=configs.db.password, db=configs.db.db))

```


不过我不明白，这个toDict函数什么时候会被调用呢？


## Day 7 - 编写MVC

mvc是model，view，controller
model，当然是models.py
view，就template文件里的模板 用jinja2 写
controller就是handlers里的handler函数

这次写一个test.html

为了这个需要修改handler函数

```python
@get('/')
async def index(request):
    users = await User.findAll()
    # return web.Response(body=b'<h1>Awesome users</h1>', content_type='text/html', charset='UTF-8')
    return {
        '__template__': 'test.html',
        'users': users
    }
```

不过我啥时候指定过templates文件夹来着？
是在app.py里initjinja函数里指定的。


```html
    <h1>All ysers</h1>
    {% for u in users%}
    <p>{{ u.name }} / {{ u.email }}</p>
    {% endfor%}
```

## Day 8 - 构建前端

这里使用了uikit来构建前端
不过我之前用过bootstrap，还用过vuejs。
我在想我有必要还用uikit吗？

因为使用了jinja2来渲染。
html本身就用了jinja2 的模板来写的。
然后jinja2来渲染进去。
不过这个语法会不会和vue冲突？

我甚至都觉得jinja2 都没必要。

先看一看别人怎么写的吧。

### 下载uikit

```python
static/
+- css/
|  +- addons/
|  |  +- uikit.addons.min.css
|  |  +- uikit.almost-flat.addons.min.css
|  |  +- uikit.gradient.addons.min.css
|  +- awesome.css
|  +- uikit.almost-flat.addons.min.css
|  +- uikit.gradient.addons.min.css
|  +- uikit.min.css
+- fonts/
|  +- fontawesome-webfont.eot
|  +- fontawesome-webfont.ttf
|  +- fontawesome-webfont.woff
|  +- FontAwesome.otf
+- js/
   +- awesome.js
   +- html5.js
   +- jquery.min.js
   +- uikit.min.js
```

可以看到3个文件夹，还下载了jquery
自己写了awesome的css和js

### jinja2 的模板

jinja2 写一个父模板，然后定义block。
然后写很多block替换进去。
感觉vuejs也能做呀。

```python
---父亲模板
{% block title%} 这里定义了一个名为title的block {% endblock %}


---子模板
{% extends 'base.html' %}

{% block title %} A {% endblock %}
```

### __base__.html 父亲模板

头部：
jialeyige block meta块，说是rss，为以后做准备。
title也加了个  block title beforehead（这是用来插入js的）
然后加了uikit，jquery，的css和js文件

body：
navbar
navbar里有a链接，li，日志，教程，源码，
还有个用户名和登出，
登陆和注册


中间是block content

尾部是固定的数据

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171105/013537036.png)


我先试一下加入vuejs

我从官网下载，然后在base的head引用了。

遇到了个问题。
我以前写的时候是webpack，新建一个vue项目。
然后直接开始写vue文件。
最后webpack自动编译成html，js，css文件。
我现在想使用在htm文件里，该怎么做？

还是说，我用webstrom新建一个vue项目，然后编译，
最后使用dist文件夹里的内容？
[vue怎么在服务器部署](https://www.zhihu.com/question/46630687)


还是说，我在html上引用js，js里写上vue的语法就行了？
这个企图失败了。

还是说，我记得body上面可以引用script，直接在这里写逻辑？
貌似这个也不可以，不知道为什么。
有没有可能是jinja2和vuejs 解释变量都在{{}}里冲突的原因？

果然是如此，所以我按照
[解决Jinja2与Vue.js的模板冲突](https://jpanj.com/2016/%E8%A7%A3%E5%86%B3jinja2%E4%B8%8EVue-js%E7%9A%84%E6%A8%A1%E6%9D%BF%E5%86%B2%E7%AA%81/)
[多个方案](https://segmentfault.com/q/1010000007035319)

按照这个方案，设置了jinja的开始和启动加了个空格，就出来了。

或者说，添加下面[这个方案](https://stackoverflow.com/questions/41082626/how-to-render-by-vue-instead-of-jinja)，表明jinja2 不渲染这个。

```python
{% raw %}{{task.body|e}}{% endraw %}
```


但是经过实验，另外写了个test的js，引入，貌似失败了。
不知道为什么。
我在想总不能以后都这样吧？

各个文件之间如何传送数据呢？

base的body里直接写上了 nav条

这里我要用iview吗？还是element？

我想先使用element

[element文档](http://element-cn.eleme.io/#/zh-CN/component/installation)

需要引入cdn。
一个css和一个js

发现了一个问题。
为什么element里的效果默认的时候不显示呢？
比如加了个按钮。
点击才启动。
貌似要把css和script放在head部分才可以。

正式开始编写前端

这里分了3个部分。
nav，和bottom 写在了base里，中间留下content。

引入了element的布局组件。
新建了一个css来引入。

navbar里有a链接，
li，日志，教程，源码，
还有个用户名和登出，
登陆和注册

用户名和登出，登陆和注册是放在右边的。
一股脑放在左边太难看了。
这个应该是layout来设置。
用了offset发现当浏览器窗口变小的时候，注册和登陆就会转移到下一楼。
我想要达到的效果是，当窗口变小，两者之间的距离会变小，而不是下一层。
发现我对element的layout认识有各种错误。

最后在el-menu里面设置了两个el-col结束了。
第二个设置了offset

用jinja的语法 if users else endif 并不会和vue冲突。

因为handler源代码里是users。所以这里如果想显示，
那么就要users[0].name才可以。

下面就是Main部分

```python
        <el-main>
            {% block content %}
            {% endblock %}
        </el-main>
```

最后footer部分

3个部分
一个是p，4个图标一排
第二个是p，copy right
第三个p，网页链接
第四个是一个大的html图标

第一个问题是间部分的高度并没有充满整个屏幕高度

发现是这个缺少高度。

el-container 这个高度设置为100%
而且html和body高度也为100%


下一个问题是，footer的内容不随着填充，footer的大小不变化。

发现footer的高度被element.style设置为60px了。
我受用了auto!important 强制修改了

图标就不加了吧。怪丑的。

### 继承一个blogs.html

只需要把content 部分block 重写就可以了。

分为两个部分，一个是文章，另一个是友情链接

#### 文章

文章部分只显示部分内容，还有个read more。
read more，我是想打开一个新连接呢？
还是想折叠显示呢？

如果是折叠，那么就用element的collapse折叠面板

如果想打开一个新连接，那么应该显示代码块，后面加一个read more链接。

还是用一个打开新连接吧。

首先把content分为两块。
左边分割为70%，文章部分
overflow: auto;
这个属性至关重要，要不然文章部分，往下拉的时候背景颜色不会改变。
height不会改变。

真是费劲。
因为css我忘光了。
所以弄得很费劲。

#### 友情链接

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171108/181303093.png)

源代码是用了ul li来做的。
但是我想试一下不同的代码。
比如用element的card功能
发现效果不好。

#### 总结



## Day 9 - 编写API

http://localhost:9000/blog/123 这是用户阅读的信息。
机器需要的是json格式的数据集。
http://localhost:9000/api/blogs/123

一个API也是一个URL的处理函数，我们希望能直接通过一个@api来把函数变成JSON格式的REST API

这里注册api是通过@get('/api/users')这个装饰器来做的。

```python
@get('/api/users')
def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = yield from User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)
```

只要返回一个dict，后续的response这个middleware就可以把结果序列化为JSON并返回。

这里需要制作一个api装饰器。
还需要一个APIError(这个以后再完善吧，还没看懂)

不过实际源代码很简单。
在handler里添加了api

```python
@get('/api/users')
async def api_get_users():
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '********'
    return dict(users=users)
```

## Day 10 - 用户注册和登录
Todo: 要做用户名重复检测

### 注册


需要一个注册的handler api和注册的页面

先写api吧

首先完善apis.py文件里apierror部分

```python
class APIValueError(APIError):
    '''
    表示输入的input error或者不符合要求。
    '''
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)
      
```

这里不太明白field是干什么用的

然后写register的api

```python
# 用户注册
@get('/register')
async def register():
    return {
        '__template__': 'register.html'
    }
```

register的html

我突然意识到，既然用vue，那么用axios就可以实现后端的数据交互啊

而且vue的数据双向绑定的话，我没必要用js来判定字符串合法性啊。

不过这个界面的vue脚本该放在哪里呢？
会不会和base里body下面的那个冲突？
base下面已经初始化了一个vue 虽然什么也没做。
因为如果每一个页面的vue代码都写在base里，太麻烦了。
但是如果缺少了这个，那么element就无法挂着。

我试着在register里，用一个新的element 生成一个vue实例。
发现没反应。

是否是因为已经绑定了#app呢？
果然没有错，我把base里的#app注释掉后，register里的就能用了。
我现在陷入了一个矛盾中。
app必须要生成一个vue，要不然header，footer无法运行。
但是绑定到app就意味着，其他界面无法绑定。

在这里其实可以做到什么呢
不用element，不用vue做base。
然后每一个界面都独自生成一个vue。

但是这样做的话，用纯css来制作footer和header和main，太麻烦了。

或者说我可以把#app当作block。
每一次转到其他界面的时候，我都要重新创建一个#app的vue。
这个做法感觉方便一些。
先这么试试吧。

其实用bootstrap制作一个header和footer也不是很麻烦。

#### register.html

首先用element的表单
model是要绑定的表单名字吧。
status-icon 是bool型，是否在输入框中显示校验结果反馈图标
rules是规则，要在下面写，是个字典
ref是什么？是表格名字，

表单验证项是el-from-item
label是表单的说明文字，prop是属性，用来在rule里检查的。

输入框是el-input
type是类型， 输入密码什么的

v-model-绑定数据
auto-complete -开或者关

规则验证里，有一个trigger，一直没想到这是什么
有change和blur选项。就是个触发器


[element表单说明](http://likaiqiang.site/2017/03/22/element-ui%E4%B8%AD%E7%9A%84%E8%A1%A8%E5%8D%95%E9%AA%8C%E8%AF%81/)

首先registerForm设置了model，
rules链接到registerRule

在el-form-item里用了prop绑定了registerRule里的userName

设计完了html和验证之后，就该设计如何跟数据库写入了。

这个是通过restfulapi实现的。
首先新建一个post的api，注册的。
然后通过js代码，把json格式的数据给发送过去。


这里submit之前自行判断了有效格式。
比如说trim()函数用来去掉空格，然后验证是否为空什么的。
虽然自己写也不是个坏事，但是验证，直接在element的表格里集成，显然更方便。

用户重复能否在这里解决掉？
可以新建一个validateUsername的函数，这个用restfulapi来搞。
然后在用户名和email添加这个检测方法

我先试一下廖雪峰在这里的代码方式。
其实可以有另外一个解决办法。
别人的代码集成了一个help文件，从api进行验证，并且返回。

在这个地方有一个廖雪峰自定义的一个函数。
就是postJSON。
这个被封装在awesome.js文件里。

既然这样，我能不能用其他第三方库来做ajax呢？
比如axios

使用了cdn，添加到了base里。

不过我在想，现在除了注册，还有登陆，还有很多很多，肯定要用到axios的
如果不封装，或者不单独放到一个代码，那么实在是太烦人了。

我可以参考这里的代码

[代码很好](https://github.com/HZNU-QUANTA/NODE-HQY/blob/master/Vue-Test/src/lib/vueHelper.js)

我如何得到表格里的数据呢？
this.registerForm.userName就可以了。
虽然我完全不知道原理。
this貌似是整个window，然后表格-字段。

下面遇到要sha1加密的问题。
这个是使用了一个加密库，我使用了cdn
[CryptoJS CDN](<script src="https://cdn.bootcss.com/crypto-js/3.1.9/sha1.js"></script>)

实在不行的话，sha1文件下载下来，本地引用也行啊。

然后发现已经成功写入了。
然后重复邮箱也发现能检测下来。

但是依然遇到个问题。
就是response返回的是字典。
axioscatch的错误是自身的传输错误。
而，重命名邮箱，并没有显示能让axio捕捉到的错误。
而是通过一个字典，返回来，结果被当成成功了。

我如何能区分呢？
两个方向：
1. 弄清楚axios能捕捉什么样的错误。
2. 在成功里判断字段，if else 解决掉。

1. 好像是我把服务器关掉后，post失败的时候能捕捉。
要改写这里，需要返回网络错误提示

错误提示要用什么呢？
消息提示？弹框？通知？
感觉弹框比较合适。

实际写代码的时候发现问题。
我无法找到vue里面的方法该如何启动呢？
我在submitform里，想要调用其他msg方法。
这个可以用this.open()就可以了。
但是经过验证，并且axios后this就不是之前的this了。

[答案看这里](https://segmentfault.com/q/1010000004939460)
在这里找到答案。
我还是对vue不熟悉。
需要好好学习。

下面就是改写重复name逻辑了。
思路是：
data里新建一个sameUser函数。
这里rule实在没啥用，value，callback就行了。
新建一个api，check email和name有没有重复。
api是要用get呢？还是post呢？
我感觉不用提交数据库所以应该是get
但是要传送两个参数，一个是value，一个是item-email或者name

email和name能否写在一个函数里？
理论上有可能，但是涉及到箭头函数，我失败了。
以后再说吧。
到此为止，注册部分已经完成。
剩下的就是登陆做好后，把注册成功后变成登陆成功。

#### post的用户注册api

这里一开始就判断接收道德参数是否为空，显然毫无意义呀。
下一步就是用接收的email，在数据库上查询。
如果查到那么就挂起APIError。
挂起的话，会如何呢？
弹窗？
还是提示？
这个需要实验一下。
再说了，这个重复检测，我觉得完全可以在register界面做呀。

下一步生成一个当前用户注册的唯一uid，
然后生成sha1——passwd

下一步创建一个用户，密码是通过sha1加密保存

然后保存这个用户到数据库用户表

最后返回一个用户信息。
这里涉及到cookie，这个需要仔细了解。




```python
@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
return r
```


### 登陆

登陆有两种主流方式，session和cookie

session就是数据存储在服务器。
cookie就是本地，储存唯一码，发送给服务器的session一对比，服务器就
知道是你了。
cookie一般用在自动登录。

由于session在用户关闭浏览器后，会话结束，就会消失，cookie随之应该也会消失。但servlet的API中提供了一些方法，可以让客户端的cookie存活的时间更久一点。这就是cookie相对于session的一大优势所在。

[知乎关于session和cookie](https://www.zhihu.com/question/19786827)

[简书里的文章](http://www.jianshu.com/p/25802021be63)

[很好的文章](http://mertensming.github.io/2016/10/19/cookie-session/)


廖雪峰的教程没用session，只用了cookie，算了，也可以吧。
只是cookie加密的方式。

#### 登陆的api-handler函数

很简单，都不值一提。
不过需要注意的事情是，函数名字，其实是用来add_router用的。
把网址和函数给捆绑。
不过之前写了程序，就自动从handlers文件里扫描添加了初始化了。
所以这个函数名现在其实用不着。

```python
# 用户登陆
@get('/login')
async def login():
    return {
        '__template__': 'login.html'
    }
```



#### 登陆界面-login.html

登陆界面 html部分和注册界面没什么区别。

有一个细节，登陆失败有两种可能性。
一个是用户不存在，另一个是密码出错。
我如果设置为用户不存在，自动检测，会不会给服务器增加负担呢？

我该怎么选择呢？想想没必要，还是提交后后台判定吧。

#### 登陆处理api-post login

也没什么需要解释的。
就是sha1的生成记着就行了。

处理函数的功能就是检测用户名和密码的正确。
使用sha1，检测。
然后返回cookie，
在这里生成一个response，这里设置cookie，然后发送给浏览器的方式
已经设置好了cookie


sha1算法说明看这里

[Day 10的梳理](http://blog.csdn.net/JosephPai/article/details/76418190)

但是这仅仅是验证密码，然后生成cookie呀。
然后该怎么做呢？
怎么写入到本地浏览器呢？

服务器又是如何拿到cookie，确定用户登录呢？

是不是每一个网页要求，都要查找cookie？判断有效性？

服务器如果每次和浏览器打交道要解密cookie的话太麻烦了。

所以利用middle在处理URL之前，把cookie解析出来。
并且把这个cookie里的登陆用户绑定到request对象上，这样以后的url处理函数
就可以直接拿到登录用户。

这里需要写两个函数，一个是app里，写一个auth_factory
另一个是揭秘cookie -cookie2user -放在handler里

这里有个问题，我突然发现廖雪峰的源代码有个没讲解，没解释的。
工厂函数data_factory
关于这个到底有什么用,我还看不明白。
集中处理request数据格（POST：’application/json’、’application/x-www-form-urlencoded’、’multipart/form-data’）

先记一下

[data_factory 1](http://blog.csdn.net/qq_38801354/article/details/73008111)

[data_factory 2](https://www.liaoxuefeng.com/discuss/001409195742008d822b26cf3de46aea14f2b7378a1ba91000/001462893855750f848630bb19c43c582fdff90f58cbee0000)

做了这些之后，网站并不能显示出用户名。
原因是在app的response_factory里，r，少了r__user__赋值的过程。
所以__user__为0

#### 退出

这个就很简单了。直接设置个logout链接。
用get在handler里设置函数，把cookie清空就可以了。


## Day 11 - 编写日志创建页

今天就做一个界面，编写blog
廖雪峰制作的是个人博客，而不是多人博客。
所以api里，个人身份是无法新建博客的。
界面应该也是看不到的。

![mark](http://oc2aktkyz.bkt.clouddn.com/markdown/20171111/231925079.png)

### 新建blog的api

很简单，post api/blogs 
都是用restful api来操作的。
接收参数，判断是否为管理员，是否为空什么的，然后新建一个Blog的实例。
save就好了。

这里和以前的api不同的是，第一个参数是request
而且把检测管理员给分离出来了。

至于路由函数，
get/manage/blogs/create
这里发送了一个id为空的字段和action为/api/blogs的字段。
这是要干嘛？我没看懂。
如果访问新建blog的界面，发送这两个字段是要干嘛？


### 新建blog的html

这里我要写文章的按钮，要放在哪里呢？

登陆成功后，在账户左面就有

我在basehtml里写上了。但是依然有个问题，
这么一来所有用户都能看到写文章的链接了。
我需要判断用户是否为管理员。

发现request.__user__这里包括了所有的数据。

进入了写博客的界面。
我非常喜欢简书的风格。
之前vue的项目是用了vue-router来组件化的。
写作界面分为好几个vue文件。

我如果想在这里这么做的话。
是否要多个html文件继承呢？
里面的数据该怎么解决呢？
如果说我按照Django的做法，一个界面有着所有的程序。
我点击书的目录的时候，等于操作了一个数据库，进行了一个操作。
那我文章目录也应该相应作出反应才可以。
这个数据我需要保存到数据库码？还是变化的时候才保存呢？

这里就有个问题了，我可以用restfulapi，post一个当前数据到数据库。

但是页面不刷新，我如何更新数据库获取的数据到文章等数据呢？

如果一个vue内，我还能重新接收数据来更新。
跨组件能做到一样的事情吗？

难道非要我，从一个vue，发送修改信号到数据库

或者说其实网址确实是变化了，只不过模板部分变化了？

一个template，继承了base，还需要继承另一个template怎么办呢？

或者说用list就能解决吗？

假设a继承于base，b继承与a。
那么b会表现什么呢？

总之没有我想的那么简单。

前后端的分离是什么意思？
[说明](https://www.bbsmax.com/A/ke5jmA2mJr/)

前后端协作是什么意思呢？

[Django和VUe协作项目](https://cloud.tencent.com/community/article/774449)

说到底，我还是不懂，如何在django这样的模板系统里，结合vue

局部动态刷新应该怎么做？


简书里，notebooks是不变的。
如果点击文章，那么会添加notes/12784884
这部分。

我怎么觉得这个光靠django做不到呢？
django是整个页面刷新不是吗？

还是说因为刷新速度太快，感觉不出来而已？
像这里说明一样
[局部刷新segmentfault说明](https://segmentfault.com/q/1010000005663229)

我需要重新创建一个模板
模板只有一个content部分。
里面的数据该如何获取呢？
是用handler直接传呢？
还是开始后用vue的js用api来获取呢？

而且我意识到我还需要修改model，因为没有books这个选项。

我到底该怎么做呢？

就设计两个页面
一个事文章列表部分，另一个是具体文章编辑页面。

要不要分离呢？
我觉得是有必要分离的，因为哪怕现在用不到，但是以后一定会用到的。

提前用这个简单的办法来测试。

#### 文章列表部分

发现不对劲。
我如果写一个列表部分。
写一个文章部分。
再写一个edit的html
再写一个基本的base的html
我该如何组合这一切？

数据流我想要的是。

##### 页面继承关系

[多层继承](http://blog.csdn.net/Super_Tiger_Lee/article/details/77855673)

base-> edit <-(list和writer)

我意识到我应该这么写

base -> (list) ->edit(writer)
或者writer写在list里面。

或者说base里就写上list
base(list) ->edit(writer)

或者
base ->(list)->(writer)->edit

但是关键问题是edit只能继承一个文件。

或者说有个include？
原来如此。
用include就可以包括了，而不是继承。

还有个super用来保持父元素。

那么应该是
base (extends)->edit <-(include)list,writer

##### 获取blog的数据

首先要获取blogs的list数据。
这个数据有几种方式获取。
首先我可以从handlers里，route的api里获取并且传送。
jinja2 如何给include里传递数据呢？

看官方的jinja2 文档，说jinja2.1开始variable能自动传过去。
[jinja2官方文档](http://jinja.pocoo.org/docs/2.10/templates/#import-visibility)

我先试一下这个方式：
首先在handlers里，路由传送blogs

发现是可以的。

handlerapi

```python
# 获取新建blog界面
@get('/manage/blogs/create')
async def manage_create_blog():
    blogs = await Blog.findAll(orderBy='created_at desc')
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs',
        'blogs': blogs
    }
```

base文件-把container，aside，main放在这里。
aside和main各有一个block

```html
<body>

<div id="app">
    <el-container>
        <el-aside>
{% block sidebar %}
{% endblock %}
        </el-aside>

        <el-main>
{% block mainbar %}
{% endblock %}
        </el-main>
    </el-container>
</div>
</body>
```

edit文件html。两个block-sidebar和mainbar
但是具体要写在list文件里，所以用了一个include


```html
{% block sidebar %}
{% include "manage_blog_bloglist.html" %}
{% endblock %}

{% block mainbar %}
{% endblock %}

```

再来就是列表的html了.
sidebar要把blogs给列表展示出来，所以用了一个for循环。

```html
{% for blog in blogs %}
    <h1>{{ blog.name }}</h1>
    <h1>{{ blog.id }}</h1>
{% endfor %}
```

第二个方式是直接用vue的方式，生成后，直接启动restfulapi，获取blogs列表渲染。
因为第一个方式很好用第二个方式不考虑了。
要不然还得写一个api，还得写一个axios需求。

##### vue-写界面

这里又遇到了个问题。

include只是直接把html粘贴过去。
无法在这里初始化vue。
只不过把这个当成html的代码块罢了。
那么vue应该直接在edit界面直接写下全部逻辑对吗？

base里的vue有没有什么可以做的？
貌似没有。

先写一个返回首页的按钮吧。

重要的是inlign-height-20px决定了按钮
a链接的text-decoration none 把按钮下面的下划线给去掉了。

下一步我是该做文集呢？还是做文章列表就可以了呢？

我其实很犹豫，因为我并不是想要用这个来完成我自己的网站。
我上次用vuejs，已经完成了很大一部分。
我是否在这里直接进行完美的样子呢？

现在handler已经存在，框架也已经完成。
以后剩下的事情，就只有编写api，编写界面而已了。

决定不写books了。
只有一个list，和文章页面，但是依然选择使用markdown编辑器。
api做到edit界面全部集成。
简书根本没有什么blogs列表之类的还需要跳转的东西。
编辑和管理全部都在一个界面完成。

返回首页按钮下面就是新建文章按钮
css怎么写我已经忘光了。异常艰难。
新建文章，我包裹在了一个div里，明明宽度，高度都是100%
但是hover 只渲染中间的a部分

还有一个问题就是，如何给一个div添加vue的方法呢？
v-on:click就可以了

新建文章按钮，按下去，就该发生什么事情呢？
下面列表更新一个list
右边写作界面换一个
网址转换过去
数据库生成一个blog实例。

网址的变化分析。
首先进入写文章之后的网址是一个writer的网址
默认为第一个书，第一个文章。

点击新建文章的话，会转到notebooks/309848/notes/90809543

对于这里来说应该是notes/9808394
会转到这里来。

这个时候应该是要经过路由处理的。
页面继承manage_blog_edit。

应该是点击文章创建按钮后，启动一个方法。
这个方法使用restfulapi，创建一个blog。
并且返回这个blog的id

然后页面转到新建blog的界面
类似于 这样

```python
@get('/blog/{id}')
def get_blog(id):
```


1. 先把新建文章div和vue的一个方法联系起来
v-on:click="create_blog"

2. 写一个api，post blogs-新建一个blog对象并且返回

```python
# 管理员新建blog文章
@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog
```

3. 新建文章的方法调用axios-上面2的方法创建一个blog并返回获取blog的id

但是因为创建blogs是写这名字，summary和content都为空才创建的。
有必要检测吗？
我觉得没有必要，直接取消这个判断。只保留一个管理员来判断非法创建就好了。

4. 新建一个get blog/{id}的api

而且我在这里还有遇到另一个问题。
因为list里blog我是从create这个api获取来的。
这个没办法继承。
所以我需要重新获取，并且渲染。
不过我在想，这样是不是每次都太浪费了？
难道就不能有个全局变量储存吗？

没办法。那就再传过来数据好了。
发现表现和我想的一模一样。

```python
# 在create的界面获取blog
@get('/manage/blogs/create/blog/{id}')
async def manage_get_blog(id):
    blog = await Blog.find(id)
    blogs = await Blog.findAll(orderBy='created_at desc')
    return {
        '__template__': 'manage_blog_createblog.html',
        'blog': blog,
        'blogs': blogs
    }
```

5. 编写继承了manage_blog_edit的一个新的html

在这里有个问题。

我需要所有新建文章在内的vue脚本。
但是我同时需要添加其他vue部分。
我是否应该在edit文件里写完全部vue脚本呢？


6. 修改list的css

- [x] list的active设置
 
```html
    <div v-for="(blog, index) in {{ blogs }}">

    <li id="blog-item" v-bind:class="{activeBlogList: index==activeListIndex}"
        v-on:click="activeListIndex=index">
        <a href="javascript:void(0)" data-type="active" class="blog-name">
            <span>{{blog.name}}--{{index}}</span>
        </a>
        <i class="el-icon-setting" v-if="index===activeListIndex"></i>
    </li>

    </div>
```

7. 设置activelist的设置弹窗

这里element的popover不知道为什么没有反应。
最后找到了popover的slot用法解决了。

[这里](https://github.com/QingWei-Li/element/commit/9260e771c14425bfce5bcac3f07d5622b9393c15)


8. 写删除方法
删除方法是用的messagebox
不过和Dialog对话框有什么区别呢？
总觉得没什么区别。
MessageBox 的作用是美化系统自带的 alert、confirm 和 prompt，因此适合展示较为简单的内容。如果需要弹出较为复杂的内容，请使用 Dialog。

我是只要确认删除。所以用messagebox就可以了。

```html
        <li id="blog-item" v-bind:class="{activeBlogList: index==activeListIndex}"
            v-on:click="activeListIndex=index">
            <a href="javascript:void(0)" data-type="active" class="blog-name">
                <span>{{blog.name}}--{{index}}</span>
            </a>
            <el-popover
                    placement="bottom"
                    width="100"
                    trigger="click">
                <span id="delete_blog" @click="delete_blog">删除文章</span>
                <i slot="reference" class="el-icon-setting" v-show="index===activeListIndex"></i>
            </el-popover>

        </li>
```

因为messagebox只不过是美化了浏览器自带的alert元素。
所以开销很小。

这里有一个bug，就是popover第一次点击的时候会一闪而过。
这个我查看了github，前几天才修复，估计需要下一个版本才能修复吧。
[bug](https://github.com/ElemeFE/element/pull/8188)


```python
            delete_blog() {
                this.$confirm('此操作将永久删除该文章, 是否继续?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
//                    这里要进行axios进行api操作
                    this.$message({
                        type: 'success',
                        message: '删除成功!'
                    });
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });
            },
```

9. 写deleteblog的api

```python
# 删除blog
@get('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    
    return dict(id=id)

```

10. 完善vue里删除的方法


不过返回来的数据都有些什么呢？
第一个检查是是否为管理员。
我先查看非管理员信息吧。

第二个就是确定删除后应该返回什么数据？blog的id？
第三个就是网络错误该怎么显示？

还有一个问题，我需要获取blog的id。get过去才可以。

activeListIndex 这个在之前点击blog列表的时候就设置为了index
我需要储存这个blogid


把这个传送过去就可以了。

@get('/api/blogs/{id}/delete')
我该如何请求这个呢？

我试过这个。

```python
axios.get('/api/blogs/{id}/delete', {
                    'id': this.activeListIndex
                })
```
发现参数id并不能传送过去。
貌似还是需要拼接网址

```python
//                    这里要进行axios进行api操作
                    axios.get('/api/blogs/' + this.activeListId + '/delete', {
//                    'id': this.activeListIndex
                })
```

而且修改了click方法。让click的时候，不光设置index，还要获取index的blog的id

```python
            setActiveList(index, blogs) {
                this.activeListIndex = index
                this.activeListId = blogs[index].id
            },
            
            v-on:click="setActiveList(index,{{ blogs }})">
```

在这里我遇到了个问题。
当我删除文章之后文章的activeindex该怎么设置？
我想直接刷新到createblog的网页，默认又是第一个blog为active

不过总之删除方法做完了。

就是每一个操作都刷新一边网页。速度简直慢得不要不要的。
简书是如何做到秒切换的？


#### 文章编辑界面

这里应该有一个是文章标题界面。
还有一个是文章summary界面。（可有可无）
还有个textarea界面









