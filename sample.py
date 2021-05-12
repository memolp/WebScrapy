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
        # print("request:::",rsp.getcode())
        with open("e://ttt_{0}.txt".format(id(self)), "w") as pf:
            pf.write("code::{0}".format('ddd'))

    def exception(self, e):
        print("run error")
        with open("e://ttt_e_{0}.txt".format(id(self)), "w") as pf:
            pf.write("code::{0}".format(e))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # 多线程
    mng = core.SessionMgr(MySessionAble, 10, is_thread=False)
    # 多进程
    # mng = core.SessionMgr(MySessionAble, 10, is_thread=False)
    # 执行多少次请求
    mng.once(2)    # 10次请求后结束
    # mng.loop(2)    # 循环执行，但最大同时只有10个执行
    # time.sleep(5)
    # mng.cancel()
    print(">>>>>>>>>>>")
