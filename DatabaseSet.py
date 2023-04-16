import sqlite3
import pandas as pd
from pandas import Series, DataFrame


class DatabaseFunction():
    def DeleteCoinDataDayAll(self):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM CoinList"
        cur.execute(sql)
        cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = '%s'" % ('CoinList'))
        conn.commit()
        conn.execute("VACUUM")
        conn.close()

    def AddCoinList(self, data):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")

        cur = conn.cursor()

        sql = "INSERT OR IGNORE INTO CoinList (CoinName) values (?)"

        cur.executemany(sql, data)
        conn.commit()
        conn.close()

    def CallCoinList(self):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT CoinName FROM CoinList"
        cur.execute(sql)

        CoinList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return CoinList

    def DeleteCoinDataMinuteAll(self):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM CoinDataMinute"
        cur.execute(sql)
        cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = '%s'" % ('CoinDataMinute'))
        conn.commit()
        conn.execute("VACUUM")
        conn.close()

    def AddCoinDataMinute(self, data):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "INSERT OR IGNORE INTO CoinDataMinute (CoinName, Time, OpenPrice, ClosePrice, HighPrice, LowPrice, " \
              "Volume) values (?, ?, ?, ?, ?, ?, ?)"
        cur.executemany(sql, data)
        conn.commit()
        conn.close()

    def CallCoinDataMinute(self):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT CoinName, Time, OpenPrice, ClosePrice, HighPrice, LowPrice, Volume FROM CoinDataMinute"
        cur.execute(sql)

        CoinData = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return CoinData

    def DeleteCoinDataDayAll(self):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM CoinDataDay"
        cur.execute(sql)
        cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = '%s'" % ('CoinDataDay'))
        conn.commit()
        conn.execute("VACUUM")
        conn.close()

    def AddCoinDataDay(self, data):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "INSERT OR IGNORE INTO CoinDataDay (CoinName, Time, OpenPrice, ClosePrice, HighPrice, LowPrice, Volume)" \
              "values (?, ?, ?, ?, ?, ?, ?)"
        cur.executemany(sql, data)
        conn.commit()
        conn.close()

    def CallCoinDataDay(self):
        conn = sqlite3.connect("CoinInfoDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT CoinName, Time, OpenPrice, ClosePrice, HighPrice, LowPrice, Volume FROM CoinDataDay"
        cur.execute(sql)

        CoinData = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return CoinData