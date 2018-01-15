import os
import sqlite3


class Crawldb:
    def __init__(self):
        self.db_file = 'lagou.db'
        self.table = 'lagou'

        self.create_db_file()
        self.conn = sqlite3.connect('lagou.db')
        self.create_table()

    def create_db_file(self):
        ''' 创建数据库文件
        '''
        if not os.path.exists(self.db_file):
            os.mknod(self.db_file)

        return True

    def create_table(self):
        ''' 创建表
        '''
        cursor = self.conn.cursor()
        sql = "DROP TABLE IF EXISTS '{table}'".format(table=self.table)
        cursor.execute(sql)

        sql = "create table %s (id integer primary key not null, area varchar(25) not null, business varchar(25) not null, salary varchar(25) not null,age varchar(25) not null, type varchar(25) not null)" % self.table
        cursor.execute(sql)
        cursor.close()
        self.conn.commit()

        return True

    def insert_data(self, args):
        ''' 插入数据
        '''
        sql = "insert into `lagou` (`area`, `business`, `salary`, `age`, `type`) values "
        sql += "('%s', '%s', '%s', '%s', '%s')" % args

        row = self.conn.cursor().execute(sql).rowcount
        self.conn.cursor().close()
        self.conn.commit()

        return row
