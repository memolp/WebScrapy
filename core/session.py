# -*- coding:utf-8 -*-

"""
  用于实现请求

  req = Request()
  req.enable_proxy()
  req.set_proxy(key, url)
  req.enable_cookies()
  req.set_cookie(key, value)
  req.set_header(key, value)
  req.enable_author()
  req.add_author(user, pass)
  req.enable_https()
  req.set_form_data(data)
  req.set_method(get/post)
  req.on_request(url)
"""

from urllib import request


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


