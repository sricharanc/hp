from lib.db.mysqldbmanager import MySqlDBManager


class TransactionalManager(object):

    def __init__(self):
        self.db_conn_obj = None

    def get_database_connection(self):
        self.db_conn_obj = MySqlDBManager()
        return self.db_conn_obj

    def end(self):
        self.db_conn_obj.close()

    def save(self):
        self.db_conn_obj.commit()

    def revertback(self):
        self.db_conn_obj.rollback()

    def __del__(self):
        self.end()
