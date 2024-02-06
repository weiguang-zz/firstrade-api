import time
from typing import List

import pandas as pd
from bs4 import BeautifulSoup, Tag
# print("done")
from firstrade import account, order, symbols
import urls
from requests.models import *

import logging
recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'
timefmt = '%y%m%d_%H:%M:%S'
logging.basicConfig(filename=time.strftime("log/application.%y%m%d.log"),
                        filemode="a",
                        level=logging.INFO,
                        format=recfmt, datefmt=timefmt)

# Create a session
ft_ss = account.FTSession(username='zheng769', password='z$H@zr3yC$_$P@K', pin='8126',
                          proxies={'https': 'http://127.0.0.1:7890', 'http': 'http://127.0.0.1:7890'})


data = {
    'accountId': '90105977'
}
for i in range(1000000):
    page_res = ft_ss.post(
                    url="https://invest.firstrade.com/cgi-bin/orderstatus", headers=urls.session_headers(), data=data
                )
    if page_res.status_code != 200:
        raise RuntimeError('wrong data')

    order_data = BeautifulSoup(
                page_res.text,
                "html.parser",
            )
    order_list_table = order_data.find(attrs={'id':'order_status'})
    tr_tags: List[Tag] = order_list_table.find('tbody').find_all('tr')
    the_orders = []
    for tr_tag in tr_tags:
        if 'id' not in tr_tag.attrs or not tr_tag.attrs['id'].startswith('90105977'):
            continue
        td_tags = tr_tag.find_all('td')
        if len(td_tags) != 9:
            continue
        quantity = td_tags[2].text.strip()
        code = td_tags[3].find('a').text.strip()
        limit_price = td_tags[5].text.strip()
        trans_type = td_tags[1].text.strip()
        status = td_tags[8].find('div').find('strong').text.strip()
        can_tag = td_tags[8].find('a', attrs={'class': 'can'})
        clordid = None
        if can_tag:
            clordid = can_tag.find('input', attrs={'name': 'clordid'}).attrs['value'].strip()

        the_orders.append({
            'clordid': clordid,
            'quantity': quantity,
            'code': code,
            'limit_price': limit_price,
            'trans_type': trans_type,
            'status': status
        })

    print(pd.DataFrame(the_orders).to_csv())
    logging.info(pd.DataFrame(the_orders).to_csv())
    print('done')
    clordid = pd.DataFrame(the_orders).iloc[0]['clordid']

    print(ft_ss.session.cookies.get_dict())
    time.sleep(2)

# data = {
#     'clordid': clordid,
#     'accountid': '90105977',
#     'ordertype': '',
# }
#
# page_res = ft_ss.post(
#                 url="https://invest.firstrade.com/cgi-bin/cxlorder", headers=urls.session_headers(), data=data
#             )
#
#
# print(page_res.text)