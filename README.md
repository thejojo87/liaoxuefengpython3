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







