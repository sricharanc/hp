from email_client.gmail_client import GmailClient
from entity.email_account import EmailAccount
from middleware.strategy.email_strategy import EmailStrategy
from models.email_dao import EmailDao
from lib.config.custom_logger import get_logger

LOG = get_logger(__name__)
CLIENT_NAME = 'gmail'

class GmailStrategy(EmailStrategy):
    """
    @summary: This class invokes the respective GmailClient and performs the necessary operations.
    """

    def __init__(self, db_obj, tran_obj, email_address):
        """
        @summary: Constructor of this class and initializes the db_obj and tran_obj for this instance.
        @param db_obj: The dbmanager object to perform db operations.
        @param tran_obj: The transaction manager object to handle transaction operations.
        """
        self.db_obj = db_obj
        self.tran_obj = tran_obj
        self.email_address = email_address
        self.email_dao = EmailDao(self.db_obj)
        self.gmail_client = GmailClient(self.email_address)

    def authenticate_new_email(self):
        """
        @summary: Enables the obtain the required authorization for the given email address.
        """
        self.gmail_client.create_authorization()

    def get_client_id(self):
        """
        @summary: Fetches the email_client_id for this client from table.
        @return: int - email_client_id
        """
        result = self.email_dao.get_email_client_details(CLIENT_NAME)
        return result['email_client_id']

    def download_emails(self):
        """
        @summary: This method enables to download the emails with the means of its respective client.
        """
        LOG.info("Entering %s:%s", GmailStrategy.__name__, self.download_emails.__name__)

        try:
            downloaded_email_account_messages_ids = self.gmail_client.download_emails(self.email_dao)
            self.tran_obj.save()
            LOG.info("Download complete for new messages.")
        except Exception:
            LOG.exception("Error when downloading the messages.")
            self.tran_obj.revertback()
            self.tran_obj.end()
            return

        # Now we can download the entire email message and save them to tables.
        for email_account_messages_id in downloaded_email_account_messages_ids:
            self.download_complete_email(email_account_messages_id)
        self.tran_obj.end()

        LOG.info("Exiting %s:%s", GmailStrategy.__name__, self.download_emails.__name__)

    def download_complete_email(self, email_account_messages_id):
        """
        @summary: This method downloads the entire email message and stores the same to the tables.
        @param email_account_messages_id: The unique id for which the email download is to be done with the client.
        """
        LOG.info("Entering %s:%s", GmailStrategy.__name__, self.download_emails.__name__)

        try:
            LOG.info("Downloading for %s", email_account_messages_id)
            self.gmail_client.download_all_email_components(email_account_messages_id)
            self.email_dao.update_message_download_completion(email_account_messages_id)
            self.tran_obj.save()
            LOG.info("Downloading completed for %s", email_account_messages_id)
        except Exception:
            LOG.exception("Error when downloading the message: %s", email_account_messages_id)
            self.tran_obj.revertback()

    def move_message(self, email_client_message_id, value):
        """
        @summary: This method moves the given message to the desired value with the help of gmail client.
        @param email_client_message_id: The unique id of the client for which the email action is to be done.
        @param value: The label value to which the message is to be moved. 
        """
        LOG.info("Entering %s:%s", GmailStrategy.__name__, self.move_message.__name__)

        self.gmail_client.move_message(email_client_message_id, value)

        LOG.info("Exiting %s:%s", GmailStrategy.__name__, self.move_message.__name__)

    def mark_message(self, email_client_message_id, value):
        """
        @summary: This method marks the given message to the desired value with the help of gmail client.
        @param email_client_message_id: The unique id of the client for which the email action is to be done.
        @param value: The value to mark either read or unread.
        """
        LOG.info("Entering %s:%s", GmailStrategy.__name__, self.mark_message.__name__)

        self.gmail_client.mark_message(email_client_message_id, value)

        LOG.info("Exiting %s:%s", GmailStrategy.__name__, self.mark_message.__name__)
