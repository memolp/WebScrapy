# WebScrapy
Py3.7 爬虫库，做一个简单的爬虫库，自己平时使用。
`还是使用3.7，这样方便后续扩展，2.7已经需要慢慢放弃了。`

### 期望开发目标
1. 支持HTTP，HTTPS
2. 支持POST，GET
3. 支持文件下载 
4. 支持Cookies持久化
5. 支持代理IP设置
6. 等等

具体开发的情况就看自己的时间吧。


#### 简单的请求方式
```python
import core
session = core.Session()
session.set_header("User-Agent", r"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36")
session.set_header("Referer", "https://www.google.com")
# session.open_proxy("https", "113.161.58.255:8080")
# session.open_cookices()
try:
    print(session.get("https://www.google.com").read())
except Exception as e:
    print(e)
```

#### 多线程/多进程
```python
import core
class MySessionAble(core.SessionRunable):
    def run(self):
        session = core.Session()
        session.get("https://www.google.com")
    def exception(self, e):
        print("run error")
# 多线程
mng = core.SessionMgr(MySessionAble, 10, is_thread=True)
# 多进程
mng = core.SessionMgr(MySessionAble, 10, is_thread=False)
# 执行多少次请求
mng.once(10)    # 10次请求后结束
mng.loop(10)    # 循环执行，但最大同时只有10个执行
```