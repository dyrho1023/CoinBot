import os
import sys
import uuid
import hashlib
import requests
import time
import threading

from datetime import datetime
from datetime import timedelta

from urllib.parse import urlencode
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from FunctionSet import *
from Slack import *
from DatabaseSet import *

a = int(3000)


class Main():
    def __init__(self):
        super().__init__()

        with open("SecretKey.txt", "r") as file:
            keys = file.readlines()
        file.close()

        self.accessKey = keys[0].rstrip()
        self.secretKey = keys[1].rstrip()
        self.serverURL = f"https://api.upbit.com"
        self.delay150ms = 150
        self.delay3s = 3000
        self.delay5s = 5000
        self.delay1h = 3600000

        self.mainAccountFunction = AccountFunction(parent=self)
        self.mainCoinFunction = CoinFunction(parent=self)
        self.mainMarketFunction = MarketFunction(parent=self)
        self.mainSlackMessage = SendSlackMessage(parent=self)
        self.mainDataControl = DatabaseFunction()
        # self.mainBackTesting = BackTestingFunction(parent=self)
        self.mainApscheduler = BlockingScheduler()
        self.coinDataScheduler = BlockingScheduler()

        self.allKRWCoinMarketName = []
        self.allKRWCoinStatus = []

        self.myAccountInitial = None
        self.myAccountCurrent = 0
        self.myAccountCash = 0

        self.myCoinListStatus = []
        self.myCoinListBalance = []
        self.myCoinListName = []
        self.myCoinListUnit = []
        self.myCoinListPrice = []
        self.myCoinListInitial = []
        self.myCoinListRate = []
        self.myCoinListCurrentRate = []

        self.nextReferenceTime = []
        self.nextReferenceDay = []
        self.referenceCount = 0
        self.referenceCoinCount = 0
        self.referenceDayCount = 0

    def AccountInitialCheck(self):
        """
        초기 투자 금액 계산
        """
        self.myAccountInitial = 0
        self.mainAccountFunction.AccountInfo(accessKey=self.accessKey, secretKey=self.secretKey,
                                                serverURL=self.serverURL)

        self.myAccountInitial = self.myAccountInitial + self.myAccountCash  # 원화 포함하여 보정

    def AccountCurrentCheck(self):
        """
        소유한 코인 상태 종합
        1) 현재가 총합
        2) 보유 Coin 상태 종합
        3) Daily 변동 비율
        4) 투자 전반적인 변동 비율
        5) 보유 Coin 변동 비율
        """

        # 보유 Coin List 규격화
        myCoinListFormat = []

        for i in range(len(self.myCoinListName)):
            myCoinListFormat.append(self.myCoinListUnit[i] + '-' + self.myCoinListName[i])

        self.mainCoinFunction.CoinCurrentData(myCoinListFormat)

        # 보유 Coin으로 계좌 전체 총합
        self.myAccountCurrent = 0
        for i in range(len(self.myCoinListPrice)):
            self.myAccountCurrent = self.myAccountCurrent + self.myCoinListPrice[i] * self.myCoinListBalance[i]

        self.myAccountCurrent = self.myAccountCurrent + self.myAccountCash

        # 보유 Coin의 Daily 상승 폭
        coinRateFormat = []
        for i in range(len(self.myCoinListName)):
            coinRateFormat.append('{: <5}'.format(self.myCoinListName[i]) + ' : ' + self.myCoinListRate[i] + '%')

        self.myAccountRate = '\n'.join(coinRateFormat)
        # print(self.myAccountRate)

        # 보유 Coin 손이익률
        myCoinRateFormat = []
        for i in range(len(self.myCoinListPrice)):
            temp = round((float(self.myCoinListPrice[i]) - float(self.myCoinListInitial[i])) / \
                    float(self.myCoinListInitial[i])*100, 2)
            myCoinRateFormat.append('{: <5}'.format(self.myCoinListName[i]) + ' : ' + str(temp) + '%')

        self.myCoinListCurrentRate = '\n'.join(myCoinRateFormat)



    def MarketStatusCheck(self):
        """
        현재 원화 Coin Market의 상황 조회
        """

        # Market 전체에 대한 상태 Notice
        self.mainCoinFunction.CoinCurrentStatus(self.allKRWCoinMarketName)


    def Slack(self):
        """
        Slack으로 메시지를 보내는 부분
        """
        self.mainSlackMessage.SendAccountInfo()


    def AnHourRepetition(self):
        """
        매 한 시간마다 반복할 Task 정립
        """
        self.AccountInitialCheck()
        self.AccountCurrentCheck()
        self.MarketStatusCheck()
        self.Slack()

    def DBClear(self):
        self.mainDataControl.DeleteCoinDataMinuteAll()
        self.mainDataControl.DeleteCoinDataDayAll()

    def DBSettingCoinDataMinute1(self):
        if self.referenceCoinCount < len(self.allKRWCoinMarketName):
            print(self.allKRWCoinMarketName[self.referenceCoinCount])
            print("Minute 진행중 :", self.allKRWCoinMarketName[self.referenceCoinCount], "0")
            self.referenceCount = 0
            self.mainCoinFunction.CoinCandleMinute(self.allKRWCoinMarketName[self.referenceCoinCount],
                                                   referenceTime='', flagDB=1)
        else:
            self.referenceCoinCount = 0
            print("Coin Data _ Minute DB가 저장되었습니다.")
            self.DBSettingCoinDataDay1()

    def DBSettingCoinDataMinute2(self):
        if self.referenceCount < 45:
            print("Minute 진행중 :", self.allKRWCoinMarketName[self.referenceCoinCount], self.referenceCount)
            threading.Timer(0.15, self.mainCoinFunction.CoinCandleMinute, (self.allKRWCoinMarketName[self.referenceCoinCount],
                                             self.nextReferenceTime, 1)).start()
        else:
            self.referenceCoinCount = self.referenceCoinCount + 1
            self.DBSettingCoinDataMinute1()

    def DBSettingCoinDataDay1(self):
        self.referenceDayCount = 0

        utcnow = datetime.utcnow()
        temputc120Days = utcnow - timedelta(31)
        utc30Days = temputc120Days.strftime("%Y-%m-%d 00:00:00")
        print(utc30Days)

        print("Day 진행중 :", self.allKRWCoinMarketName[self.referenceDayCount])
        self.mainCoinFunction.CoinCandleDay(self.allKRWCoinMarketName[self.referenceDayCount], referenceDay=utc30Days,
                                            flagDB=1)

    def DBSettingCoinDataDay2(self):
        if self.referenceDayCount < len(self.allKRWCoinMarketName):
            print("Day 진행중 :", self.allKRWCoinMarketName[self.referenceDayCount])
            threading.Timer(0.15, self.mainCoinFunction.CoinCandleDay, (self.allKRWCoinMarketName[self.referenceDayCount],
                                                                        '', 1)).start()
        else:
            print("Coin Data _ Day DB가 저장되었습니다.")

    def TradingStart(self):
        ## Initial Condition
        self.AccountInitialCheck()
        self.AccountCurrentCheck()
        self.mainMarketFunction.MarketCoin(flagDB=0)

        ## Repeition
        # self.mainApscheduler.add_job(self.AnHourRepetition, 'cron', hour='*')
        self.mainApscheduler.add_job(self.AnHourRepetition, 'cron', minute='*')
        self.mainApscheduler.start()


if __name__ == '__main__':
    mainFunction = Main()
    print("======== Option ========")
    print("1. Coin Info 요약")
    print("2. DB Setting 동작")
    print("3. Machine Learning 동작")
    print("4. 프로그램 종료")
    print("========================\n")

    option = int(input("옵션을 입력하세요 "))

    if option == 1:
        print("1. Coin Info 요약")
        mainFunction.TradingStart()
    elif option == 2:
        print("2. DB Setting 동작")
        # mainFunction.DBClear()
        mainFunction.mainMarketFunction.MarketCoin(flagDB=1)
        # mainFunction.DBSettingCoinDataMinute1()
        mainFunction.DBSettingCoinDataDay1()
    elif option == 3:
        print("3. Machine Learning 동작")
    elif option == 4:
        print("4. 프로그램 종료")
    else:
        print("다시 선택해주세요")

#     app = QApplication(sys.argv)
#     windowMain = MainWindow()
#     windowMain.show()
#
#     app.exec_()



# data = []
# currency_data.append(res.json()[0])
# currency_data.append(res.json()[1])
# print("보유 자본")
# print(f"{currency_data[0]['currency']}: {currency_data[0]['balance']}")
# print(currency_data[0])
# print(currency_data[0])
#
# jwt_token = jwt.encode(payload, secret_key)
# authorize_token = 'Bearer {}'.format(jwt_token)
# headers = {"Authorization": authorize_token}
#
# res = requests.get(server_url + "/v1/accounts", headers=headers)
#
# print(res.json())
# print(type(aa))
# print(len(aa))