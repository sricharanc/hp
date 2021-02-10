from lib.config.custom_logger import get_logger


LOG = get_logger(__name__)

class FilterDao(object):

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_new_filter(self, rule_name, rule_value):
        query = 'insert into filter_rules(rule_name, rule_value) values(%s, %s)'
        query_args = (rule_name, rule_value)
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False, returnprikey=1)

    def get_all_filters(self):
        query = 'select filter_rules_id, rule_name, rule_value from filter_rules'
        return self.db_conn.processquery(query=query, fetch=True)

    def get_eligible_emails_for_filtering(self, filter_rules_id):
        query = 'select email_account_messages_id from email_account_messages  where email_account_messages_id not in ' \
                '(select email_account_messages_id from email_message_filter_rules_status where filter_rules_id = %s) ' \
                'and message_download = 1'
        query_args = (filter_rules_id,)
        return self.db_conn.processquery(query=query, arguments=query_args, fetch=True)

    def create_email_message_filter_rules_status(self, email_account_messages_id, filter_rules_id):
        query = 'insert into email_message_filter_rules_status values(%s, %s)'
        query_args = (email_account_messages_id, filter_rules_id)
        self.db_conn.processquery(query=query, arguments=query_args, fetch=False)
