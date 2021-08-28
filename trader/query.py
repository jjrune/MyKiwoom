import os
import sys
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.static import db_stg


class Query:
    def __init__(self, qlist):
        self.windowQ = qlist[0]
        self.workerQ = qlist[1]
        self.queryQ = qlist[7]
        self.con = sqlite3.connect(db_stg)
        self.cur = self.con.cursor()
        self.Start()

    def __del__(self):
        self.con.close()

    def Start(self):
        while True:
            query = self.queryQ.get()
            if type(query) == str:
                try:
                    self.cur.execute(query)
                except Exception as e:
                    self.windowQ.put([1, f'시스템 명령 오류 알림 - 입력값이 잘못되었습니다. {e}'])
                else:
                    self.con.commit()
            elif type(query) == list:
                query[0].to_sql(query[1], self.con, if_exists=query[2], chunksize=1000)
