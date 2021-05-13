# -*- coding:utf-8 -*-

import core


# session = core.Session()
# session.set_header("User-Agent", r"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36")
# session.set_header("Referer", "https://www.google.com")
# # session.open_proxy("https", "113.161.58.255:8080")
# # session.open_cookices()
# try:
#     print(session.get("https://www.google.com").read())
# except Exception as e:
#     print(e)

import time
import multiprocessing

class MySessionAble(core.SessionRunable):
    def run(self):
        session = core.Session()
        session.set_header("User-Agent", r"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36")
        session.set_header("Referer", "https://www.baidu.com")
        rsp = session.get("https://www.baidu.com")
        print("request:::",rsp.getcode())

    def exception(self, e):
        print("run error")


if __name__ == '__main__':
    # 多进程需要额外加上
    multiprocessing.freeze_support()
    # 多线程
    mng = core.SessionMgr(MySessionAble, 10, is_thread=True)
    # 多进程
    # mng = core.SessionMgr(MySessionAble, 10, is_thread=False)
    # 执行多少次请求
    # mng.once(1)    # 10次请求后结束
    mng.loop(1)    # 循环执行，但最大同时只有10个执行
