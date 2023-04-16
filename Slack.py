import json
import requests
import time


class FormatMessage():
    def KoreaUnit(self, number):
        amount = str(number)

        if number > 9999:
            return '{0}만 {1}원'.format(amount[-8:-4], amount[-4:])
        else:
            return '{0}원'.format(amount[-4:])


class SendSlackMessage():
    def __init__(self, parent):
        self.parent = parent

        with open("SecretKey.txt", "r") as file:
            keys = file.readlines()
        file.close()

        self.token = keys[2].rstrip()
        self.headers = {
            "Content-type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}"
        }

        self.true = 1
        self.false = 0
        self.formatMessage = FormatMessage()

    def SendAccountInfo(self):
        # 보유 코인 요약
        currentRate = {}
        currentRate["short"] = "self.true,"
        currentRate["title"] = "Daily Status"
        currentRate["value"] = "{}".format(self.parent.myAccountRate)
        jsonCurrentRate = json.dumps(currentRate)

        # 보유 코인 이익률
        myCoinRate = {}
        myCoinRate["short"] = "self.true,"
        myCoinRate["title"] = "Original Status"
        myCoinRate["value"] = "{}".format(self.parent.myCoinListCurrentRate)
        print("정보가 송신되었습니다.")
        jsonMyCoinRate = json.dumps(myCoinRate)

        data = {
            "token": self.token,
            "channel": "#coin",
            "attachments":  [{
                "color": "#3385FF",
                "pretext": "Coin Information",
                "title": "정시 Coin 알림 ",
                "text": "ㅤ\n",
                "fields": [
                    {
                        "short": self.true,
                        "title": "추정 자산",
                        "value": self.formatMessage.KoreaUnit(int(self.parent.myAccountCurrent)) + "ㅤ\n"
                    },
                    {
                        "short": self.true,
                        "title": "투자 자산",
                        "value": self.formatMessage.KoreaUnit(int(self.parent.myAccountInitial)) + "ㅤ\n"
                                 + "ㅤ"
                    },
                    {
                        "short": self.true,
                        "title": "KRW Coin 요약",
                        "value": "상승 : " + str(self.parent.allKRWCoinStatus[0]).zfill(3) + " 종목 \n"
                                 + "하락 : " + str(self.parent.allKRWCoinStatus[1]).zfill(3) + " 종목 \n"
                                 + "보합 : " + str(self.parent.allKRWCoinStatus[2]).zfill(3) + " 종목 \n"
                                 + "ㅤ"
                    },
                    {
                        "short": self.true,
                        "title": "보유 Coin 요약",
                        "value": "상승 : " + str(self.parent.myCoinListStatus[0]).zfill(3) + " 종목 \n"
                                 + "하락 : " + str(self.parent.myCoinListStatus[1]).zfill(3) + " 종목 \n"
                                 + "보합 : " + str(self.parent.myCoinListStatus[2]).zfill(3) + " 종목 \n"
                                 + " "
                    },
                    eval(jsonCurrentRate),
                    eval(jsonMyCoinRate),
            ],
                "ts": time.time()
            }]
        }

        URL = "https://slack.com/api/chat.postMessage"
        res = requests.post(URL, headers=self.headers, data=json.dumps(data))
