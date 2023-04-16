import numpy
import random
import datetime
from DatabaseSet import *

class GeneticAlgorithm():
    def __init__(self):
        self.valueK = 0                      # 변동성 돌파 비율
        self.volumeRatio = 0                 # 거래량 배율
        self.volumeDuration = 0              # 거개량 기간
        self.earnRatio = 0                   # 익절 배율
        self.looseRatio = 0                  # 손절 배율
        self.budget = 200000                 # 종목 당 투입 자금 : 20만
        self.noTrading = 0                   # 매도 후 보류 시간
        self.holdTrading = 0                 # 매수 후 보류 시간
        self.maxHoldingDuration = 0          # 최대 보유 기간
        self.balance = 1000000               # 잔고 100 만원

        ## Genetic Algorithm Variable
        self.poolSize = 100                  # 유전자 Pool 크기
        self.superior = 20                   # 유성 유전자 Pool 크기
        self.generationSize = 10000          # 진화 세대 횟수
        self.parameters = []

        ## Function Import
        self.dataControl = DatabaseFunction()

        ## Initial Setting
        self.CoinList = []
        self.CoinDataDay = []
        self.CoinDataMinute = []

    def GAInitialization(self):
        self.valueK = round(random.random(), 3)                 # 변동성 돌파 비율
        self.volumeRatio = random.randrange(1, 100)             # 거래량 배율
        self.volumeDuration = random.randrange(1, 90)           # 거래량 기간
        self.earnRatio = round(random.random(), 3)              # 익절 배율
        self.looseRatio = round(random.random(), 3)             # 손절 배율
        self.budget = 200000                                    # 종목 당 투입 자금 : 20만
        self.noTrading = random.randrange(0, 120)               # 매도 후 보류 시간
        self.holdTrading = random.randrange(0, 120)             # 매수 후 보류 시간
        self.maxHoldingDuration = random.randrange(0, 24)       # 최대 보유 시간
        self.parameters = [self.valueK, self.volumeRatio, self.volumeDuration, self.earnRatio, self.looseRatio,
                           self.budget, self.noTrading, self.holdTrading, self.maxHoldingDuration]
        return self.parameters

    # def GAFitnessCalculation(self):
    def FitnessBaseSetting(self):
        self.CoinList = self.dataControl.CallCoinList()
        # tempCoinDataMinute = self.dataControl.CallCoinDataMinute()
        tempCoinDataDay = self.dataControl.CallCoinDataDay()
        #
        # for i in tempCoinList:
        #     tempList = list(i)
        #     self.CoinList = self.CoinList + tempList
        # print(self.CoinList)
        # 2021-10-10T00:00:00

        utcnow = datetime.datetime.utcnow()
        temputc120Days = utcnow - datetime.timedelta(60)
        utc120Days = temputc120Days.strftime("%Y-%m-%dT00:00:00")
        # print(utcnow)
        print(utc120Days)
        #
        # print(self.CoinList[0][0] == tempCoinDataDay[0][0])
        # print("원래 값", self.CoinList[0][0], tempCoinDataDay[0][0])

        for i in range(len(self.CoinList)):
            print("여기냐", i, self.CoinList[i][0])
            tempArray = []
            for j in range(len(tempCoinDataDay)):
                if tempCoinDataDay[j][0] == self.CoinList[i][0]:
                    tempArray.append(tempCoinDataDay[j])
            self.CoinDataDay.append(tempArray)
        print(self.CoinDataDay[0][1])
        print(len(self.CoinDataDay[1]))
            # print(self.CoinDataDay[i][0])

        # print(self.CoinDataDay[0])

        # for i in range(len(tempCoinDataDay)):
        #     if tempCoinDataDay[i][1] == utc120Days:
        #         print(tempCoinDataDay[i][1])
        # print(tempCoinDataDay[0][1])
        # print(len(tempCoinDataDay))

        # j = 0
        # tempData = []
        # for i in len(tempCoinData):
        #     tempData = int(tempCoinData[i][2]) + tempCoinList[i][3]
        #     j = j + 1
        #     if (j % 10000) == 0:
        #         print(j)
        # print(int(tempCoinData[367000][2])+int(tempCoinData[367000][3]))
        # print(tempCoinData[367000])
        #
        # return np.array(solution).dot(parameters)

    def GAOverall(self):
        ## initializae solution pool
        self.currentSolutionPool = []
        tempPool = []
        for i in range(self.poolSize):
            tempPool = self.GAInitialization()
            self.currentSolutionPool.append(tempPool)
        print(self.currentSolutionPool[0])
        print(self.currentSolutionPool[1])

        self.FitnessBaseSetting()


    # for i in range(0, 10):
    #     ## 현재 솔루션 중에서 가장 성과가 좋은 놈만 남기고 모두 버림
    #     new_parents = sorted(current_solution_pool, key=calculate_fitness, reverse=True)[:4]
    #     print(f"optimal fitness in {i:0>2d} generation: {calculate_fitness(new_parents[0])}")
    #     ## 간단하게 크로스오버 세팅
    #     crossovers = [
    #         new_parents[0][:3]+new_parents[1][3:],
    #         new_parents[1][:3]+new_parents[0][3:],
    #         ]
    #     ## 뮤테이션 세팅
    #     mutations = [
    #         list(np.array(new_parents[0])+np.random.normal(0, 1, 6)),
    #         list(np.array(new_parents[0])+np.random.normal(0, 1, 6)),
    #     ]
    #     current_solution_pool = new_parents + crossovers + mutations
    #
    #


if __name__ == '__main__':
    geneticProcess = GeneticAlgorithm()
    geneticProcess.GAOverall()
