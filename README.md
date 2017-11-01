"# liaoxuefengpython3" 

[github地址](https://github.com/thejojo87/liaoxuefengpython3)

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