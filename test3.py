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
# requestfrom: orderstatus
# accountId: 90105977
# option_orderbar_clordid: DF21ACF00016609
# option_orderbar_accountid: 90105977
# submitOrders: 1
# previewOrders:
# haspreviewedOrder: 0
# currOpenQty: 1
# transactionType: BO
# contracts: 1
# underlyingsymbol: JD
# expdate: 02/02/24
# strike: 21.00
# callputtype: C
# priceType: 2
# limitPrice: 0.05
# duration: 0
# qualifier: 0
    'requestfrom': 'orderstatus',
    'accountId': '90105977',
    'option_orderbar_clordid': 'FF22B6U00023936',
    'option_orderbar_accountid': '90105977',
    'submitOrders': '1',
    'previewOrders': '',
    'haspreviewedOrder': '0',
    'currOpenQty': '2',
    'transactionType': 'BO',
    'contracts': '2',
    'underlyingsymbol': 'JD',
    'expdate': '02/16/24',
    'strike': '21.00',
    'callputtype': 'C',
    'priceType': '2',
    'limitPrice': '0.11',
    'duration': '0',
    'qualifier': '0'
}
page_res = ft_ss.post(
                url="https://invest.firstrade.com/cgi-bin/option_cxlrpl_response", headers=urls.session_headers(), data=data
            )
if page_res.status_code != 200:
    raise RuntimeError('wrong data')

# order_data = BeautifulSoup(
#             page_res.text,
#             "xml",
#         )

print(page_res.text)