import logging
from enum import Enum
from typing import List

import pandas as pd
from bs4 import BeautifulSoup, Tag

from firstrade import urls


class PriceType(str, Enum):
    """
    This is an :class: 'enum.Enum' that contains the valid price types for an order.
    """

    LIMIT = "2"
    MARKET = "1"
    STOP = "3"
    STOP_LIMIT = "4"
    TRAILING_STOP_DOLLAR = "5"
    TRAILING_STOP_PERCENT = "6"


class Duration(str, Enum):
    """This is an :class:'~enum.Enum' that contains the valid durations for an order."""

    DAY = "0"
    GT90 = "1"
    PRE_MARKET = "A"
    AFTER_MARKET = "P"
    DAY_EXT = "D"


class OrderType(str, Enum):
    """
    This is an :class:'~enum.Enum'
    that contains the valid order types for an order.
    """

    BUY = "B"
    SELL = "S"
    SELL_SHORT = "SS"
    BUY_TO_COVER = "BC"


class Order:
    """
    This class contains information about an order.
    It also contains a method to place an order.
    """

    def __init__(self, ft_session):
        self.ft_session = ft_session
        self.order_confirmation = {}


    def order_status(self):
        # todo process the partial filled condition
        data = {
            'accountId': '90105977'
        }
        page_res = self.ft_session.post(
            url="https://invest.firstrade.com/cgi-bin/orderstatus", headers=urls.session_headers(), data=data
        )
        if page_res.status_code != 200:
            raise RuntimeError('wrong data')

        order_data = BeautifulSoup(
            page_res.text,
            "html.parser",
        )
        order_list_table = order_data.find(attrs={'id': 'order_status'})
        tr_tags: List[Tag] = order_list_table.find('tbody').find_all('tr')
        the_orders = {}
        for tr_tag in tr_tags:
            if 'id' not in tr_tag.attrs or not tr_tag.attrs['id'].startswith('90105977'):
                continue
            td_tags = tr_tag.find_all('td')
            if len(td_tags) != 9:
                continue
            quantity = int(td_tags[2].text.strip())
            code = td_tags[3].find('a').text.strip()
            limit_price = td_tags[5].text.strip()
            trans_type = td_tags[1].text.strip()
            status = td_tags[8].find('div').find('strong').text.strip()
            can_tag = td_tags[8].find('a', attrs={'class': 'can'})
            clordid = None
            if can_tag:
                clordid = can_tag.find('input', attrs={'name': 'clordid'}).attrs['value'].strip()

            the_order = {
                'clordid': clordid,
                'quantity': quantity,
                'code': code,
                'limit_price': limit_price,
                'trans_type': trans_type,
                'status': status
            }

            the_key = "{}_{}_{}".format(code, limit_price, trans_type)
            the_orders[the_key] = the_order

        return the_orders


    def cancel_option_order(self, account_id, clordid):

        data = {
            'clordid': clordid,
            'accountid': account_id,
            'ordertype': '',
        }

        page_res = self.ft_session.post(
            url="https://invest.firstrade.com/cgi-bin/cxlorder", headers=urls.session_headers(), data=data
        )

        if page_res.status_code != 200:
            raise RuntimeError('wrong data')

        # 校验订单状态
        if '/cgi-bin/main#/cgi-bin/cxlorder' not in page_res.text or clordid in page_res.text:
            logging.error('cancel error, request:{}, response:{}'.format(data, page_res.text))
            raise RuntimeError('cancel error')

        return


    def update_option_order_price(
            self,
            clordid,
            account,
            symbol,
            option_order_type,
            quantity,
            expire_date: pd.Timestamp,
            strike,
            option_type,
            new_limit_price):
        # todo change the quantity
        expire_date_str = expire_date.tz_convert("America/New_York").strftime("%m/%d/%Y")
        strike_str = "%.2f" % strike
        if option_type not in ['C', 'P']:
            raise RuntimeError('wrong option type')
        limit_price_str = str(round(new_limit_price, 2))
        if option_order_type not in ['BO', 'SO', 'BC', 'SC']:
            raise RuntimeError('wrong option order type')

        data = {
            'requestfrom': 'orderstatus',
            'accountId': account,
            'option_orderbar_clordid': clordid,
            'option_orderbar_accountid': account,
            'submitOrders': '1',
            'previewOrders': '',
            'haspreviewedOrder': '0',
            'currOpenQty': '1',
            'transactionType': option_order_type,
            'contracts': '{}'.format(quantity),
            'underlyingsymbol': '{}'.format(symbol),
            'expdate': expire_date_str,
            'strike': strike_str,
            'callputtype': option_type,
            'priceType': '2',
            'limitPrice': limit_price_str,
            'duration': '0',
            'qualifier': '0'
        }
        page_res = self.ft_session.post(
            url="https://invest.firstrade.com/cgi-bin/option_cxlrpl_response", headers=urls.session_headers(), data=data
        )
        if page_res.status_code != 200:
            raise RuntimeError('wrong data')

        order_data = BeautifulSoup(
                    page_res.text,
                    "xml",
                )
        order_confirmation = {}
        order_success = order_data.find("success").text.strip()
        order_confirmation["success"] = order_success
        action_data = order_data.find("actiondata").text.strip()
        if order_success != "Yes":
            logging.error("place order error {}".format(page_res.text))
            raise RuntimeError('place order error {}'.format(action_data))

        return order_confirmation

    def place_option_order(
        self,
        account,
        symbol,
        option_order_type,
        quantity,
        expire_date: pd.Timestamp,
        strike,
        option_type,
        limit_price,
        dry_run=True,
    ):
        """
        Builds and places an order.
        :attr: 'order_confirmation`
        contains the order confirmation data after order placement.

        Args:

            option_order_type,
            quantity,
            expire_date,
            strike,
            option_type,
            price_type,
            limit_price,
            duration: Duration,
            dry_run (bool, optional): Whether you want the order to be placed or not.
                                      Defaults to True.

        Returns:
            Order:order_confirmation: Dictionary containing the order confirmation data.
        """

        if dry_run:
            previewOrders = "1"
            submitOrder = ""
        else:
            previewOrders = ""
            submitOrder = "1"

        expire_date_str = expire_date.tz_convert("America/New_York").strftime("%m/%d/%Y")
        strike_str = "%.3f" % strike
        if option_type not in ['C', 'P']:
            raise RuntimeError('wrong option type')
        limit_price_str = str(round(limit_price, 2))
        if option_order_type not in ['BO', 'SO', 'BC', 'SC']:
            raise RuntimeError('wrong option order type')

        data = {
            "submiturl": "/cgi-bin/optionorder_request",
            "orderbar_clordid": "",
            "orderbar_accountid": "",
            "optionorderpage": "yes",
            "submitOrders": submitOrder,
            "previewOrders": previewOrders,
            "lotMethod": "1",
            "accountType": "2",
            "quoteprice": "",
            "viewederror": "",
            "stocksubmittedcompanyname1": "",
            "opt_choice": "SO",
            "accountId": account,
            "transactionType": option_order_type,
            "contracts": str(quantity),
            "underlyingsymbol": symbol,
            "expdate": expire_date_str,
            "strike": strike_str,
            "callputtype": option_type,
            "priceType": "2",
            "limitPrice": limit_price_str,
            "duration": "0",
            "qualifier": "",
            "cond_symbol0_0": "",
            "cond_type0_0": "2",
            "cond_compare_type0_0": "2",
            "cond_compare_value0_0": "",
            "cond_and_or0": "1",
            "cond_symbol0_1": "",
            "cond_type0_1": "2",
            "cond_compare_type0_1": "2",
            "cond_compare_value0_1": "",
            "optionspos_dropdown1": "",
            "transactionType2": "",
            "contracts2": "",
            "underlyingsymbol2": "",
            "expdate2": "",
            "strike2": "",
            "optionspos_dropdown2": "",
            "transactionType3": "",
            "contracts3": "",
            "underlyingsymbol3": "",
            "expdate3": "",
            "strike3": "",
            "netprice_sp": "",
            "qualifier_sp": "",
            "optionspos_dropdown3": "",
            "transactionType4": "",
            "contracts4": "",
            "underlyingsymbol4": "",
            "expdate4": "",
            "strike4": "",
            "transactionType5": "",
            "contracts5": "",
            "underlyingsymbol5": "",
            "expdate5": "",
            "strike5": "",
            "netprice_st": "",
            "qualifier_st": "",
            "optionspos_dropdown": "",
            "contracts10": "",
            "expdate11": "",
            "strike11": "",
            "netprice_ro": "",
            "qualifier_ro": "",
            "opt_u_symbol": "",
            "mleg_close_dropdown": "",
            "transactionType6": "",
            "contracts6": "",
            "underlyingsymbol6": "",
            "expdate6": "",
            "strike6": "",
            "transactionType7": "",
            "contracts7": "",
            "underlyingsymbol7": "",
            "expdate7": "",
            "strike7": "",
            "transactionType8": "",
            "contracts8": "",
            "underlyingsymbol8": "",
            "expdate8": "",
            "strike8": "",
            "transactionType9": "",
            "contracts9": "",
            "underlyingsymbol9": "",
            "expdate9": "",
            "strike9": "",
            "netprice_bf": "",
            "qualifier_bf": "",
        }

        order_data = BeautifulSoup(
            self.ft_session.post(
                url=urls.option_order_bar(), headers=urls.session_headers(), data=data
            ).text,
            "xml",
        )
        order_confirmation = {}
        order_success = order_data.find("success").text.strip()
        order_confirmation["success"] = order_success
        action_data = order_data.find("actiondata").text.strip()
        if order_success != "No":
            # Extract the table data
            table_start = action_data.find("<table")
            table_end = action_data.find("</table>") + len("</table>")
            table_data = action_data[table_start:table_end]
            table_data = BeautifulSoup(table_data, "xml")
            titles = table_data.find_all("th")
            data = table_data.find_all("td")
            for i, title in enumerate(titles):
                order_confirmation[f"{title.get_text()}"] = data[i].get_text()
            if not dry_run:
                start_index = action_data.find(
                    "Your order reference number is: "
                ) + len("Your order reference number is: ")
                end_index = action_data.find("</div>", start_index)
                order_number = action_data[start_index:end_index]
            else:
                start_index = action_data.find('id="') + len('id="')
                end_index = action_data.find('" style=', start_index)
                order_number = action_data[start_index:end_index]
            order_confirmation["orderid"] = order_number
        else:
            order_confirmation["actiondata"] = action_data
        order_confirmation["errcode"] = order_data.find("errcode").text.strip()
        self.order_confirmation = order_confirmation
        return order_confirmation

    def place_order(
        self,
        account,
        symbol,
        price_type: PriceType,
        order_type: OrderType,
        quantity,
        duration: Duration,
        price=0.00,
        dry_run=True,
    ):
        """
        Builds and places an order.
        :attr: 'order_confirmation`
        contains the order confirmation data after order placement.

        Args:
            account (str): Account number of the account to place the order in.
            symbol (str): Ticker to place the order for.
            order_type (PriceType): Price Type i.e. LIMIT, MARKET, STOP, etc.
            quantity (float): The number of shares to buy.
            duration (Duration): Duration of the order i.e. DAY, GT90, etc.
            price (float, optional): The price to buy the shares at. Defaults to 0.00.
            dry_run (bool, optional): Whether you want the order to be placed or not.
                                      Defaults to True.

        Returns:
            Order:order_confirmation: Dictionary containing the order confirmation data.
        """

        if dry_run:
            previewOrders = "1"
        else:
            previewOrders = ""

        if price_type == PriceType.MARKET:
            price = ""

        data = {
            "submiturl": "/cgi-bin/orderbar",
            "orderbar_clordid": "",
            "orderbar_accountid": "",
            "stockorderpage": "yes",
            "submitOrders": "1",
            "previewOrders": previewOrders,
            "lotMethod": "1",
            "accountType": "1",
            "quoteprice": "",
            "viewederror": "",
            "stocksubmittedcompanyname1": "",
            "accountId": account,
            "transactionType": order_type,
            "quantity": quantity,
            "symbol": symbol,
            "priceType": price_type,
            "limitPrice": price,
            "duration": duration,
            "qualifier": "0",
            "cond_symbol0_0": "",
            "cond_type0_0": "2",
            "cond_compare_type0_0": "2",
            "cond_compare_value0_0": "",
            "cond_and_or0": "1",
            "cond_symbol0_1": "",
            "cond_type0_1": "2",
            "cond_compare_type0_1": "2",
            "cond_compare_value0_1": "",
        }

        order_data = BeautifulSoup(
            self.ft_session.post(
                url=urls.orderbar(), headers=urls.session_headers(), data=data
            ).text,
            "xml",
        )
        order_confirmation = {}
        order_success = order_data.find("success").text.strip()
        order_confirmation["success"] = order_success
        action_data = order_data.find("actiondata").text.strip()
        if order_success != "No":
            # Extract the table data
            table_start = action_data.find("<table")
            table_end = action_data.find("</table>") + len("</table>")
            table_data = action_data[table_start:table_end]
            table_data = BeautifulSoup(table_data, "xml")
            titles = table_data.find_all("th")
            data = table_data.find_all("td")
            for i, title in enumerate(titles):
                order_confirmation[f"{title.get_text()}"] = data[i].get_text()
            if not dry_run:
                start_index = action_data.find(
                    "Your order reference number is: "
                ) + len("Your order reference number is: ")
                end_index = action_data.find("</div>", start_index)
                order_number = action_data[start_index:end_index]
            else:
                start_index = action_data.find('id="') + len('id="')
                end_index = action_data.find('" style=', start_index)
                order_number = action_data[start_index:end_index]
            order_confirmation["orderid"] = order_number
        else:
            order_confirmation["actiondata"] = action_data
        order_confirmation["errcode"] = order_data.find("errcode").text.strip()
        self.order_confirmation = order_confirmation
        return order_confirmation
