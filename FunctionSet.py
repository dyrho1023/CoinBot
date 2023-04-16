import os
import sys
import jwt
import uuid
import hashlib
import requests
from urllib.parse import urlencode, unquote

from datetime import datetime
from DatabaseSet import *

# from PyQt5.QtWidgets import *


class AccountFunction():
    def __init__(self, parent=None):
        self.parent = parent
        self.accessKey = None
        self.secretKey = None
        self.serverURL = None

    def AccountInfo(self, accessKey, secretKey, serverURL):
        """
        내 계좌로 소유하고 있는 코인 현황
        """
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.serverURL = serverURL

        payload = {
            'access_key': accessKey,
            'nonce': str(uuid.uuid4()), }

        jwtToken = jwt.encode(payload, secretKey)
        authorizeToken = 'Bearer {}'.format(jwtToken)
        header = {"Authorization": authorizeToken}

        tempResult = requests.get(serverURL + "/v1/accounts", headers=header)
        result = tempResult.json()
        # print(result)
        data = []
        coinListName = []
        coinListUnit = []
        coinListBalance = []
        accountInitial = 0
        coinListInitial = []

        for i in range(len(result)):
            data.append(result[i])
            coinListName.append(data[i]['currency'])
            coinListUnit.append(data[i]['unit_currency'])
            coinListBalance.append(data[i]['balance'])
            coinListInitial.append(data[i]['avg_buy_price'])

            accountInitial = accountInitial + float(data[i]['balance'])*float(data[i]['avg_buy_price'])

        priceZero = []
        for i in range(len(result)-1, -1, -1):           # 구입 가격이 0원인 자산 제외
            if float(data[i]['avg_buy_price']) == 0:
                priceZero.append(i)
                del coinListName[i]
                del coinListUnit[i]
                del coinListBalance[i]
                del coinListInitial[i]

        self.parent.myCoinListName = coinListName
        self.parent.myCoinListUnit = coinListUnit
        self.parent.myCoinListBalance = list(map(float, coinListBalance))
        self.parent.myAccountCash = float(data[0]['balance'])
        self.parent.myAccountInitial = accountInitial
        self.parent.myCoinListInitial = coinListInitial


class CoinFunction():
    def __init__(self, parent=None):
        self.parent = parent
        self.dataControl = DatabaseFunction()

    def CoinCurrentData(self, checkList):     # Coin의 Data 조회 및 계산
        url = "https://api.upbit.com/v1/ticker"
        headers = {"Accept": "application/json"}

        querystring = {"markets": checkList}

        result = requests.request("GET", url, headers=headers, params=querystring).json()
        # result = tempResult.json()

        data = []
        coinPrice = []
        coinRate = []
        coinStatus = []
        for i in range(len(result)):
            data.append(result[i])
            coinPrice.append(data[i]['trade_price'])
            coinRate.append(round(data[i]['signed_change_rate']*100,2))
            coinStatus.append(data[i]['change'])

        self.parent.myCoinListPrice = list(map(float, coinPrice))
        self.parent.myCoinListRate = list(map(str, coinRate))

        self.parent.myCoinListStatus.append(coinStatus.count('RISE'))
        self.parent.myCoinListStatus.append(coinStatus.count('FALL'))
        self.parent.myCoinListStatus.append(coinStatus.count('EVEN'))

    def CoinCurrentStatus(self, checkList):  # 마켓 전체의 Coin의 상태 조회 (보합/상승/하락)
        url = "https://api.upbit.com/v1/ticker"
        headers = {"Accept": "application/json"}
        querystring = {"markets": checkList}

        result = requests.request("GET", url, headers=headers, params=querystring).json()
        # result = tempResult.json()

        data = []
        coinStatus = []
        self.parent.allKRWCoinStatus = []
        for i in range(len(result)):
            data.append(result[i])
            coinStatus.append(data[i]['change'])

        self.parent.allKRWCoinStatus.append(coinStatus.count('RISE'))
        self.parent.allKRWCoinStatus.append(coinStatus.count('FALL'))
        self.parent.allKRWCoinStatus.append(coinStatus.count('EVEN'))

        # self.parent.tempCoinPrice = list(map(float, coinPrice))

    def CoinCandleMinute(self, coinName, referenceTime, flagDB):
        url = "https://api.upbit.com/v1/candles/minutes/5"

        # print(referenceTime)
        querystring = {"market": coinName, "to": referenceTime, "count": "200"}
        headers = {"Accept": "application/json"}

        result = requests.request("GET", url, headers=headers, params=querystring).json()

        data = []
        reData = []
        coinCandleData = []

        for i in range(len(result)):
            data.append(result[i])
            if flagDB == 1:
                reData = (data[i]['market'], data[i]['candle_date_time_utc'], data[i]['opening_price'],
                          data[i]['trade_price'], data[i]['high_price'], data[i]['low_price'],
                          data[i]['candle_acc_trade_volume'])
            #        (CoinName, Time, OpenPrice, ClosePrice, HighPrice, LowPrice, Volume
                coinCandleData.append(reData)

        # print(coinCandleData)
        self.dataControl.AddCoinDataMinute(coinCandleData)

        tempReferenceTime = list(data[len(result)-1]['candle_date_time_utc'])
        tempReferenceTime[10] = " "
        self.parent.nextReferenceTime = ''.join(tempReferenceTime)
        # print("kst값 : ", data[len(result)-1]['candle_date_time_kst'])
        # print("utc값 : ", self.parent.nextReferenceTime)

        self.parent.referenceCount = self.parent.referenceCount + 1
        self.parent.DBSettingCoinDataMinute2()

    def CoinCandleDay(self, coinName, referenceDay, flagDB):
        url = "https://api.upbit.com/v1/candles/days"

        # print(referenceTime)
        querystring = {"market": coinName, "to": referenceDay, "count": "90"}
        headers = {"Accept": "application/json"}

        result = requests.request("GET", url, headers=headers, params=querystring).json()

        data = []
        reData = []
        coinCandleData = []

        for i in range(len(result)):
            data.append(result[i])
            if flagDB == 1:
                reData = (data[i]['market'], data[i]['candle_date_time_utc'], data[i]['opening_price'],
                          data[i]['trade_price'], data[i]['high_price'], data[i]['low_price'],
                          data[i]['candle_acc_trade_volume'])
                #        (CoinName, Time, OpenPrice, ClosePrice, HighPrice, LowPrice, Volume
                coinCandleData.append(reData)

        # print(coinCandleData)
        self.dataControl.AddCoinDataDay(coinCandleData)

        self.parent.referenceDayCount = self.parent.referenceDayCount + 1
        self.parent.DBSettingCoinDataDay2()


class MarketFunction():
    def __init__(self, parent=None):
        self.parent = parent
        self.dataControl = DatabaseFunction()

    def MarketCoin(self, flagDB):
        """
        Market에서 거래가능한 Coin 이름을 확인 하고, DB에 저장
        """
        url = "https://api.upbit.com/v1/market/all"
        headers = {"Accept": "application/json"}
        querystring = {"isDetails": "true"}

        tempResult = requests.request("GET", url, headers=headers, params=querystring)
        result = tempResult.json()

        data = []
        allCoinMarketName = []
        for i in range(len(result)):
            data.append(result[i])
            allCoinMarketName.append(data[i]['market'])

        search = 'KRW'
        for i in range(len(allCoinMarketName)):
            if search in allCoinMarketName[i]:
                self.parent.allKRWCoinMarketName.append(allCoinMarketName[i])
                if flagDB == 1:
                    self.dataControl.AddCoinList([(allCoinMarketName[i],)])
                else:
                    pass
            else:
                pass

        if flagDB == 1:
            print("Coin List DB가 저장되었습니다.")
        else:
            pass



        #
        # for i in range(len(result)):
        #     print(len(result))
        #     print(result[i])

        #     coinPrice.append(data[i]['trade_price'])
        #
        # self.parent.myCoinPrice = coinPrcie



        # AccountCurrent = 0
        # for i in range(len(result)):
        #     AccountCurrent =AccountCurrent + float(data[i]['balance'])*float(data[i]['avg_buy_price'])
        #     print(result[i]['market'])

        #
        #
        #
        #
        #
        # data = []
        # accountInitial = 0

        # for i in range(len(result)):
        #     data.append(result[i])
        #     print(data[i])
        #
        # print(data[0]['trade_price'], data[1]['trade_price'])



        #
        # self.AccountCheckRefeat(accessKey=self.accessKey, secretKey=self.secretKey, serverURL=self.serverURL)

    # def AccountCheckRefeat(self, accessKey, secretKey, serverURL):
    #     self.accessKey1 = accessKey
    #     self.secretKey1 = secretKey
    #     self.serverURL1 = serverURL
    #     delay3s = 1000              # TR 제한 10분 200개
    #
    #     print("a")
    #     print(self.serverURL1)
    #
    #     QTimer.singleShot(delay3s, lambda: self.AccountCheck(accessKey=self.accessKey1, secretKey=self.secretKey1,
    #                                                          serverURL=self.serverURL1))

