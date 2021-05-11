# -*- coding:utf-8 -*-

import core


session = core.Session()
session.set_header("User-Agent", r"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36")
session.set_header("Referer", "https://www.google.com")
session.open_proxy("https", "14.20.235.194:808")
# session.open_cookices()
# print(session.get("https://www.google.com").read())