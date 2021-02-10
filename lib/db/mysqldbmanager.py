import datetime
import re

import mysql.connector

from lib.config.common_config import DB_CREDENTIALS
from lib.config.custom_logger import get_logger

LOG = get_logger(__name__)

class MySqlDBManager(object):

    def __init__(self):
        self.connection_id = None
        self.conn = self.create_connection()

    def create_connection(self):
        # Getting Configuration Parameters
        try:
            host = DB_CREDENTIALS['host']
            port = DB_CREDENTIALS['port']
            retry = DB_CREDENTIALS['retry']
            database = DB_CREDENTIALS['database']
            user = DB_CREDENTIALS['user']
            passwd = DB_CREDENTIALS['password']
        except Exception:
            LOG.error("exception while fetching config variable.")
            raise
        for trial in range(int(retry)):
            try:
                # Creating MySQL Connection
                self.conn = mysql.connector.connect(host=host,
                                                    user=user,
                                                    passwd=passwd,
                                                    db=database,
                                                    port=port,
                                                    autocommit=False)

                # Retrieving connection id from MySQL server
                self.connection_id = self.conn.connection_id
                return self.conn

            except (mysql.connector.DatabaseError,
                    mysql.connector.IntegrityError,
                    mysql.connector.InterfaceError,
                    mysql.connector.InternalError,
                    mysql.connector.OperationalError,
                    mysql.connector.PoolError,
                    mysql.connector.DataError,
                    mysql.connector.NotSupportedError,
                    mysql.connector.ProgrammingError) as ex:
                LOG.error(" Exception Occurred in creating Connection. exception no: %s", ex.errno)
                if trial == int(retry)-1:
                    LOG.error("Exception Occurred in creating Connection and retry limit reached")
                    raise

    def getcursor(self):
        '''
           Creating cursor from the connection.
        '''
        if self.conn:
            return self.conn.cursor(dictionary=True)

    def is_connected(self):
        if self.conn.is_connected():
            return True
        else:
            return False

    def ping(self, reconnect=False):
        self.conn.ping(reconnect)

    def __formatargs(self, query, arguments):
        if isinstance(arguments, tuple):
            arguments = list(arguments)
        res_args = []
        if isinstance(arguments, list):
            end_idx = 0
            query = re.sub('\([ ]*%[ ]*s[ ]*\)', '(%s)', query)
            for i, value in enumerate(arguments):
                if isinstance(value, tuple) or isinstance(value, list):
                    len_ = len(value)
                    find_idx = query.index('(%s)', end_idx)
                    end_idx = find_idx + len("(%s)")
                    query = list(query)
                    query[find_idx:end_idx] = '(%s' + ', %s' * (len_ - 1) + ')'
                    query = ''.join(query)
                    for ele in value:
                        res_args.append(ele)
                else:
                    res_args.append(value)
        else:
            pass

        if not res_args:
            res_args = arguments
        return query, res_args

    def processquery(self, query, count=0, arguments=None, fetch=True, returnprikey=0, do_not_log_resultset=0):
        '''
        :Notes: execute the given query respective of given argument.
        :Args: query: query to execute
        :Args: count: if select query, howmany rows to return
        :Args: arguments: arguments for the query.
        :Args: fetch: select query - True , update/insert query - False
        :Args: returnprikey: insert query - 1, update query - 0
        '''
        query_start_time = None
        query_end_time = None
        try:
            res = None
            result_set = None
            curs = self.getcursor()
            if arguments:
                query, arguments = self.__formatargs(query, arguments)
            # Calculate query execution time
            query_start_time = datetime.datetime.now()
            curs.execute(query, arguments)

            if fetch:
                result_set = curs.fetchall()
                if count == 1 and len(result_set) >= count:
                    res = result_set[0]
                elif count == 1 and len(result_set) < count:
                    res = {}
                elif len(result_set) >= count > 1:
                    res = result_set[0:count]
                else:
                    res = result_set
                query_end_time = datetime.datetime.now()
            else:
                if returnprikey:
                    res = curs.lastrowid
                else:
                    res = curs.rowcount
                query_end_time = datetime.datetime.now()
            curs.close()
            return res
        except (mysql.connector.DataError,
                mysql.connector.IntegrityError,
                mysql.connector.NotSupportedError,
                mysql.connector.ProgrammingError) as ex:
            LOG.error("ConnectionID :: " +
                             str(self.connection_id) +
                             " Exception Occurred while executing the query")
            raise
        except (mysql.connector.DatabaseError,
                mysql.connector.InterfaceError,
                mysql.connector.InternalError,
                mysql.connector.OperationalError,
                mysql.connector.PoolError) as ex:
            LOG.error("ConnectionID :: " +
                             str(self.connection_id) +
                             " Exception Occurred in creating Connection")
            raise
        except ValueError as ex:
            LOG.error("ConnectionID :: " +
                             str(self.connection_id) +
                             " Value Error Occurred while executing the query")
            raise
        except Exception as ex:
            LOG.error("ConnectionID :: " +
                             str(self.connection_id) +
                             " Un-handled exception in DB Manager processquery")
            raise

    def commit(self):
        """
            Committing the changes
        """
        if self.conn:
            self.conn.commit()

    def rollback(self):
        """
            Rollback the changes
        """
        if self.conn:
            self.conn.rollback()

    def close(self):
        """Closing the Connection

        """
        if self.conn:
            self.conn.close()