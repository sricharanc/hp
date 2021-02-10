from datetime import datetime

from lib.config.custom_logger import get_logger


LOG = get_logger(__name__)

class EmailDao(object):

    def __init__(self, db_conn):
        self.db_conn = db_conn

#     def check_email_account(self, email_address):
#         query = 'select * from email_account where email_address = %s'
#         query_args = (email_address, )
#         return self.db_conn.processquery(query=query, arguments=query_args, fetch=True)

    def fetch_all_email_accounts(self):
        query = 'select email_address, email_client_name as email_client from email_account join email_client using(email_client_id)'
        return self.db_conn.processquery(query=query, fetch=True)

    def get_specific_email_account(self, email_address):
        query = 'select email_account_id, email_address, email_client_name as email_client, last_update_id from ' \
            'email_account join email_client using(email_client_id) where email_address = %s'
        query_args = (email_address, )
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True, count=1)

    def get_email_account_with_email_account_id(self, email_account_id):
        query = 'select email_address, email_client_name as email_client from ' \
            'email_account join email_client using(email_client_id) where email_account_id = %s'
        query_args = (email_account_id, )
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True, count=1)


    def get_email_client_details(self, client_name):
        query = 'select email_client_id from email_client where email_client_name = %s'
        query_args = (client_name, )
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True, count=1)

    def get_email_account_message(self, email_account_messages_id):
        query = 'select * from email_account_messages where email_account_messages_id = %s'
        query_args = (email_account_messages_id, )
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True, count=1)

    def create_email_account(self, email_account_obj):
        query = 'insert into email_account(email_address, email_client_id, created_datetime) values(%s, %s, %s)'
        query_args = (email_account_obj.email_address, email_account_obj.email_client_id, datetime.now())
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False)

    def create_email_message(self, email_message_obj):
        query = 'insert into email_account_messages(email_account_id, email_client_message_id, email_datetime) '\
                'values(%s, %s, %s)'
        query_args = (email_message_obj.email_account_id, email_message_obj.email_client_message_id,
                      email_message_obj.email_datetime)
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=1)

    def create_email_message_component(self, email_message_component_obj):
        query = 'insert into email_message_components(email_account_messages_id, component_type, component_value) '\
                'values(%s, %s, %s)'
        query_args = (email_message_component_obj.email_account_messages_id,
                      email_message_component_obj.component_type,
                      email_message_component_obj.component_value)
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=0)

    def get_email_components(self, email_account_messages_id):
        query = 'select * from email_message_components where email_account_messages_id = %s'
        query_args = (email_account_messages_id, )
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True)

    def create_email_message_body(self, email_message_component_obj):
        query = 'insert into email_message_body(email_account_messages_id, email_message) values(%s, %s)'
        query_args = (email_message_component_obj.email_account_messages_id, email_message_component_obj.component_value)
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=0)

    def get_email_message_body(self, email_account_messages_id):
        query = 'select * from email_message_body where email_account_messages_id = %s'
        query_args = (email_account_messages_id, )
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True, count=1)

    def update_email_account_email_client_message_id(self, email_account_id, email_client_message_id):
        query = 'update email_account set last_update_id=%s where email_account_id = %s'
        query_args = (email_client_message_id, email_account_id)
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=0)

    def update_message_download_completion(self, email_account_messages_id):
        query = 'update email_account_messages set message_download=1 where email_account_messages_id = %s'
        query_args = (email_account_messages_id, )
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=0)

    def update_email_datetime(self, email_account_messages_id, email_datetime):
        query = 'update email_account_messages set email_datetime=%s where email_account_messages_id = %s'
        query_args = (email_datetime, email_account_messages_id)
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=0)