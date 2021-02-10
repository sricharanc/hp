import abc
from entity.email_account import EmailAccount
from models.email_dao import EmailDao

class EmailStrategy(object):
    """
    @summary: The base strategy class for different email agents.
    """

    def __init__(self, db_obj, tran_obj, email_address):
        self.db_obj = db_obj
        self.tran_obj = tran_obj
        self.email_address = email_address

    @abc.abstractmethod
    def get_client_id(self):
        return

    @abc.abstractmethod
    def download_emails(self):
        return

    def create_email_account(self):
        email_account_obj = EmailAccount(self.email_address, self.get_client_id())
        EmailDao(self.db_obj).create_email_account(email_account_obj)

    @abc.abstractmethod
    def move_message(self, email_client_message_id, value):
        return

    @abc.abstractmethod
    def mark_message(self, email_client_message_id, value):
        return
