from typing import List

import pandas as pd
from bs4 import BeautifulSoup, Tag
#
# s = """
# <response>
# <order>
# <success>No</success>
# <redirect></redirect>
# <actiondata>此订单的预估总额超出您账户的可用购买力。存入的新资金可能需要5个工作日过账。</actiondata>
# <errcode>1041</errcode>
# <action>updateDiv</action>
# </order>
# </response>
# """
#
# order_res = BeautifulSoup(
#             s,
#             "xml",
#         )
#
# print("done")
from firstrade import account, order, symbols
import urls
from requests.models import *
# Create a session
ft_ss = account.FTSession(username='zheng769', password='z$H@zr3yC$_$P@K', pin='8126',
                          proxies={'https': 'http://127.0.0.1:7890', 'http': 'http://127.0.0.1:7890'})


# 更新订单

data = {
    'clordid': 'FF25AD800009195',
    'accountid': '90105977',
    'ordertype': '',
}

headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Host": "invest.firstrade.com",
        "Referer": "https://invest.firstrade.com/cgi-bin/main",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }


# curl "https://invest.firstrade.com/cgi-bin/cxlorder" ^
#   -H "Accept: */*" ^
#   -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" ^
#   -H "Connection: keep-alive" ^
#   -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" ^
#   -H "Cookie: home=accountBalances^%^2C1^%^2C1^%^3Bhome_positions^%^2C1^%^2C2^%^3BtotalValueChart^%^2C1^%^2C4^%^3BeDocs^%^2C1^%^2C4^%^3BorderStatus^%^2C1^%^2C3^%^3Bmovers^%^2C1^%^2C1^%^3BmarketOverview^%^2C1^%^2C2^%^3Bnews^%^2C1^%^2C4^%^3Bhome_watchlist^%^2C1^%^2C3; ft_locale=en-us; last_active=1706865467854; _scid=ddbfd447-860c-4a12-8c10-f303272bebe8; _ga=GA1.1.1045920673.1700642979; _fbp=fb.1.1700642980499.1291433680; _gcl_au=1.1.662738564.1700642978.938448287.1701430600.1701430599; ajs_anonymous_id=5d3a2bb8-74a1-465e-87b5-f2989acbad46; FT_default_page=stock_order; FT_NEW_VIEW=viewed; _gcl_aw=GCL.1702373219.CjwKCAiApuCrBhAuEiwA8VJ6Jsx0J28J-9BzUFuuefUqdelwGQKyLaHXXpZgFheBHmMqjeEHGRPWBxoCFdQQAvD_BwE; _uetvid=117b6080891411eeac00bb096ad4bf24; FT_AT=BDB2A1B0C618B37102AB13CA4718C8B5E1AA9FB38F7FA7DEEF421D7085B939FE; TS01912bbd026=0118ed6d3f289ab3d56ac750ee49586af1406ca2f8a3b8369994d492eb347838f13233d336441ffec4f5de16e19cf6bb0bb517cdccc7e5cab7a8b470072512c0bce4d23c46; _sctr=1^%^7C1706716800000; _rdt_uuid=1700642978331.3d77c85d-800c-4a67-88ac-9971f580c9c5; _scid_r=ddbfd447-860c-4a12-8c10-f303272bebe8; _ga_4C67L0MN9N=GS1.1.1706857814.11.0.1706857817.57.0.0; pubLocale=en_us; FT_LST=; SID=2DB09BE65B1AA95D583D061F0A51C9F7DEAFA404A8594FF59C1C5D6BB083DC54; FT_LBF2=^!JCFj5Xz0kLhqocTBfc7XfJIW8RcOOrUeXkjvCBR9mi6jRSuEzb69VtujAutEK0pnXzaChIGyQZV5Cw==; TS01912bbd=01d7aa468c77b21b48052773da135ade2696266230dd1fbd4358c28e290fb1eb0bb24e1fe310db4f88eb2825ed8feba0518094a949241a74bb0e0c9eebe8403138638eb2019bea75ad48a3f178fc5b8ae2a25b9a2773decfd809ebe69dbfb3618080f76e26e4972c26f9fa8421b6e56e1d6e6085b00395831532626ab610ab938387be81a56f9310ffc20b4463c7c414a842b9fdaa993c56f2dcac492ba47c86b2582a16280e34d3fd7e722f7a8efbf13fac4bbc32" ^
#   -H "Origin: https://invest.firstrade.com" ^
#   -H "Referer: https://invest.firstrade.com/cgi-bin/main" ^
#   -H "Sec-Fetch-Dest: empty" ^
#   -H "Sec-Fetch-Mode: cors" ^
#   -H "Sec-Fetch-Site: same-origin" ^
#   -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" ^
#   -H "X-Requested-With: XMLHttpRequest" ^
#   -H "sec-ch-ua: ^\^"Not_A Brand^\^";v=^\^"8^\^", ^\^"Chromium^\^";v=^\^"120^\^", ^\^"Google Chrome^\^";v=^\^"120^\^"" ^
#   -H "sec-ch-ua-mobile: ?0" ^
#   -H "sec-ch-ua-platform: ^\^"Windows^\^"" ^
#   --data-raw "clordid=DF21ACF00016749&accountid=90105977&ordertype=" ^
#   --compressed

page_res = ft_ss.post(
                url="https://invest.firstrade.com/cgi-bin/cxlorder", headers=urls.session_headers(), data=data
            )

if page_res.status_code != 200:
    raise RuntimeError('wrong data')

# order_data = BeautifulSoup(
#             page_res.text,
#             "xml",
#         )

print(page_res.text)