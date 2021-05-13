# -*- coding:utf-8 -*-

"""
  用于实现请求
"""

import sys
import time
import inspect

from urllib import request
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent import futures


class SessionImpl(object):
    """
    """
    K_PROXY_HANDLER         = 1     # 代理
    K_COOKIE_HANDLER        = 2     # 缓存
    K_AUTH_HANDLER          = 3     # 账号验证（代理的依然是1）
    K_REDIRECT_HANDLER      = 4     # 重定向
    def __init__(self, **kwargs):
        # 记录当前的缓存请求
        self.__cache_handlers = {}

    def _create_proxy_handler(self, key, proxy_url):
        """
        创建代理请求
        @param key: "http" or "https"
        @param proxy_url: "ip:port" or "http://ip:port" or "user:password@ip:port"
        """
        proxy_cfg = {}
        proxy_cfg[key] = proxy_url
        proxy_handler = request.ProxyHandler(proxy_cfg)
        self.__cache_handlers[SessionImpl.K_PROXY_HANDLER] = proxy_handler

    def _create_cookie_handler(self, cookiejar=None):
        """
        创建cookies请求
        @param cookiejar: 默认http.cookiejar.CookieJar
        """
        cookie_header = request.HTTPCookieProcessor(cookiejar)
        self.__cache_handlers[SessionImpl.K_COOKIE_HANDLER] = cookie_header
    
    def _create_auth_handler(self, passwdmgr, is_proxy=False):
        """
        创建具有客户端授权的请求
        @param passwdmgr: HTTPPasswordMgrWithDefaultRealm对象
        @param is_proxy: 是否是代理
        """
        if is_proxy:
            proxy_handler = request.ProxyBasicAuthHandler(passwdmgr)
            self.__cache_handlers[SessionImpl.K_PROXY_HANDLER] = proxy_handler
        else:
            auth_handler = request.HTTPBasicAuthHandler(passwdmgr)
            self.__cache_handlers[SessionImpl.K_AUTH_HANDLER] = proxy_handler

    def _create_redirect_handler(self):
        """
        创建支持重定向的请求
        """
        redirect_handler = request.HTTPRedirectHandler()
        self.__cache_handlers[SessionImpl.K_REDIRECT_HANDLER] = redirect_handler

    def _create_passwd_mgr(self, user, passwd, url):
        """
        创建密码管理对象
        @param user: 账号
        @param passwd: 密码
        @param url: 地址
        """
        passwdmgr = request.HTTPPasswordMgrWithDefaultRealm()
        passwdmgr.add_password(None, url, user, password)
        return passwdmgr
    
    def open_proxy(self, key, url):
        """
        打开代理设置
        """
        self._create_proxy_handler(key, url)

    def open_proxy_auth(self, url, user, passwd):
        """
        打开代理设置- 指定账号密码
        """
        passwdmgr = self._create_passwd_mgr(user, passwd, url)
        self._create_auth_handler(passwdmgr, is_proxy=True)

    def open_cookices(self, cookiejar=None):
        """
        打开cookie设置
        """
        self._create_cookie_handler(cookiejar)

    def open_http_auth(self, url, user, passwd):
        """
        打开客户端验证
        """
        passwdmgr = self._create_passwd_mgr(user, passwd, url)
        self._create_auth_handler(passwdmgr)

    def open_redirect(self):
        """
        打开重定向
        """
        self._create_redirect_handler()

    def _open(self, req, timeout=30, opener=None):
        """
        打开的接口，外部不用调用
        """
        if opener is None:
            opener = self.build_opener()
        return opener.open(req, timeout=timeout)

    def build_opener(self):
        """
        创建opener
        """
        return request.build_opener(*list(self.__cache_handlers.values()))


class Session(SessionImpl):
    def __init__(self):
        super(Session, self).__init__()
        self.__cache_headers = {}
        self.__cache_data = None
        self.__cache_opener = None

    def set_cookie(self, key, value):
        pass

    def set_header(self, key, value):
        """
        设置请求头
        """
        self.__cache_headers[key] = value

    def get(self, url, timeout=30, use_cache_opener=False):
        """
        GET请求
        """
        if not use_cache_opener or self.__cache_opener is None:
            self.__cache_opener = self.build_opener()
        req = request.Request(url, data=self.__cache_data, headers=self.__cache_headers, method="GET")
        return self._open(req, timeout, opener=self.__cache_opener)

    def post(self, url, timeout=30, use_cache_opener=False):
        """
        POST请求
        """
        if not use_cache_opener or self.__cache_opener is None:
            self.__cache_opener = self.build_opener()
        req = request.Request(url, data=self.__cache_data, headers=self.__cache_headers, method="POST")
        return self._open(req, timeout, opener=self.__cache_opener)


class SessionRunable:
    """
    Session多线程/进程执行包装类
    """
    def __init__(self):
        pass

    def run(self, **kwargs):
        pass

    def exception(self, e):
        pass


def _run_thread_impl(runable_cls, **kwargs):
    """
    线程执行包装
    """
    # 先生成对象
    runable_obj = runable_cls()
    try:
        # 执行
        runable_obj.run(**kwargs)
    except Exception as e:
        # 异常反馈
        runable_obj.exception(e)


def get_class_from_module(module_name, class_name):
    cls_list = inspect.getmembers(module_name, inspect.isclass)
    for name, _ in cls_list:
        if name == class_name:
            return 

def _run_process_impl(run_cls_name, run_cls_module, **kwargs):
    """
    进程执行包装，由于进程启动不能像线程那样可以传递对象
    """
    try:
        # 非专业实现...
        # 先根据模块名找到对应的模块
        # 然后根据类名获取类
        # 最后创建类对象
        runable_module = sys.modules[run_cls_module]
        runable_cls  = getattr(runable_module, run_cls_name)
        runable_obj = runable_cls()
        try:
            # 执行
            runable_obj.run(**kwargs)
        except Exception as e:
            # 异常反馈
            runable_obj.exception(e)
    except Exception as e:
        # 这个理论上没人看得到。。。
        print("[process] error:{0}".format(e))


class SessionMgr:
    """
    支持多线程或者多进程执行Session请求的封装类
    """
    def __init__(self, runable_cls, num_of_pool, is_thread=True):
        """
        @param runable_cls: 请求的包装类，用于实现外部控制
        @param num_of_pool: 池的数量，线程or进程
        @param is_thread: 默认为线程，False则使用进程
        """
        if not issubclass(runable_cls, SessionRunable):
            raise TypeError("runable_cls must be extends from SessionRunable")
        self.mSessionRunableCls = runable_cls
        self.mPoolObj = None
        self.mRunningFlag = False
        self.mIsThreadMode = is_thread
        if is_thread:
            self.mPoolObj = ThreadPoolExecutor(num_of_pool)
        else:
            self.mPoolObj = ProcessPoolExecutor(num_of_pool)

    def once(self, num, **kwargs):
        """
        单次执行
        @param num: 同时执行多少个，每个执行完就退出
        @param kwargs: 外部传给执行类的参数
        """
        jobs = []
        # 区分线程和进程的启动方式
        if self.mIsThreadMode:
            _run_impl = _run_thread_impl
            _run_cls = self.mSessionRunableCls
        else:
            _run_impl = _run_process_impl
            _run_cls = self.mSessionRunableCls.__name__
            _run_mod = self.mSessionRunableCls.__module__

        for i in range(num):
            if self.mIsThreadMode:
                jobs.append(self.mPoolObj.submit(_run_impl, _run_cls, **kwargs))
            else:
                jobs.append(self.mPoolObj.submit(_run_impl, _run_cls, _run_mod, **kwargs))
        futures.wait(jobs)
        
    
    def loop(self, num, **kwargs):
        """
        循环执行
        @param num: 同时执行num个，每个执行完继续执行
        @param kwargs: 外部传给执行类的参数
        """
        self.mRunningFlag = True
        enable_task_num = num
        jobs = []
        # 区分线程和进程的启动方式
        if self.mIsThreadMode:
            _run_impl = _run_thread_impl
            _run_cls = self.mSessionRunableCls
        else:
            _run_impl = _run_process_impl
            _run_cls = self.mSessionRunableCls.__name__
            _run_mod = self.mSessionRunableCls.__module__

        while self.mRunningFlag:
            for i in range(enable_task_num):
                if self.mIsThreadMode:
                    jobs.append(self.mPoolObj.submit(_run_impl, _run_cls, **kwargs))
                else:
                    jobs.append(self.mPoolObj.submit(_run_impl, _run_cls, _run_mod, **kwargs))
            enable_task_num = 0
            while self.mRunningFlag and enable_task_num == 0:
                temp_done_jobs = []
                for job in jobs:
                    if job.done():
                        enable_task_num += 1
                        temp_done_jobs.append(job)
                # 都没有完成就等待
                if enable_task_num == 0:
                    time.sleep(1)
                # 移除已完成的
                for job in temp_done_jobs:
                    jobs.remove(job)

