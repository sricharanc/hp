from lib.transactional_manager import TransactionalManager
from models.email_dao import EmailDao
from middleware.email_client_mapper_factory import EmailClientMapperFactory
from lib.config.custom_logger import get_logger

LOG = get_logger(__name__)


class EmailManager(object):
    """
    @summary: This class provides functionalities to perform required operations over a given email account.
    """

    def __init__(self, email_address, email_client):
        """
        @summary: Constructor where the email_address and email_client are initialized.
        @param email_address: str - The required email address for which the operations are to be performed.
        @param email_client: str - The client to which the given email_address is associated with.
        """
        self.email_address = email_address
        self.email_client = email_client
        self.tran_obj = None
        self.db_obj = None

    def _get_strategy_obj(self):
        """
        @summary: This method will connect with EmailClientMapperFactory and returns the EmailStrategy object.
        @return: An instance of the associated EmailStrategy.
        """
        factory_obj = EmailClientMapperFactory()
        strategy = factory_obj.get_email_strategy(self.email_client)
        return strategy(self.db_obj, self.tran_obj, self.email_address)

    def _create_transaction(self):
        """
        @summary: Creates a new transaction object in order to perform the required db operations.
        @return: None
        """
        try:
            if not self.tran_obj:
                LOG.info("Creating transaction.")
                self.tran_obj = TransactionalManager()
                self.db_obj = self.tran_obj.get_database_connection()
        except Exception as e:
            LOG.error("Exception while creating a transaction: %s", e)
            raise

    def authorize_new_email(self):
        """
        @summary: This method is used to create authorization for new email account.
        Once this method is executed, we will have an authorization available to make further actions
        over the authorized email account.
        """
        LOG.info("Entering %s:%s", EmailManager.__name__, self.authorize_new_email.__name__)

        self._create_transaction()
        try:
            if not self._check_email_exists():
                LOG.info("Email account is not present, hence creating it.")
                self._create_email_account()
                self._authenticate_email()
                self.tran_obj.save()
        except Exception:
            self.tran_obj.revertback()
            LOG.exception("Exception when authorizing the new email")
        finally:
            self.tran_obj.end()

        LOG.info("Exiting %s:%s", EmailManager.__name__, self.authorize_new_email.__name__)

    def _check_email_exists(self):
        """
        @summary: Checks whether the email_address is already present for the given email address.
        Returns True if email already exists else False.
        @return: Boolean.
        """
        email_dao_obj = EmailDao(self.db_obj)
        if email_dao_obj.get_specific_email_account(self.email_address):
            return True
        return False

    def _authenticate_email(self):
        """
        @summary: Authenticates the new email for the email_address.
        """
        strategy_obj = self._get_strategy_obj()
        strategy_obj.authenticate_new_email()

    def _create_email_account(self):
        """
        @summary: Creates the new email account for the given email address.
        """
        strategy_obj = self._get_strategy_obj()
        strategy_obj.create_email_account()
        LOG.info("Email account created.")

    def process_message_download(self):
        """
        @summary: This method will downloads the messages from the email client and stores it to the tables.
        """
        LOG.info("Entering %s:%s", EmailManager.__name__, self.process_message_download.__name__)

        try:
            self._create_transaction()
            strategy_obj = self._get_strategy_obj()
            strategy_obj.download_emails()
        except Exception:
            LOG.exception("Exception occured while processing download for email: %s", self.email_address)

        LOG.info("Exiting %s:%s", EmailManager.__name__, self.process_message_download.__name__)


class BulkEmailManager(object):
    """
    @summary: This class provides functionalities to perform required operations over a set of email accounts.
    """

    def process_message_download_all_emails(self):
        """
        @summary: This method enables us to download messages for all the email accounts present in the table.
        After fetching the emails, it processes each email account individually to download messages.
        """
        LOG.info("Entering %s:%s", BulkEmailManager.__name__, self.process_message_download_all_emails.__name__)

        email_accounts = self._fetch_all_email_accounts()
        for email_account in email_accounts:
            try:
                LOG.info("Downloading messages for %s", email_account['email_address'])
                email_manager_obj = EmailManager(email_account['email_address'], email_account['email_client'])
                email_manager_obj.process_message_download()
            except Exception:
                LOG.exception("Exception occured while processing download for email: %s", email_account['email_address'])

        LOG.info("Exiting %s:%s", BulkEmailManager.__name__, self.process_message_download_all_emails.__name__)

    def _fetch_all_email_accounts(self):
        """
        @summary: This method connects with database and fetches all the email accounts and returns the data.
        @return: Tuple of Dictionaries containing the email account information.
        """
        tran_obj = TransactionalManager()
        db_obj = tran_obj.get_database_connection()
        email_dao_obj = EmailDao(db_obj)
        email_accounts = email_dao_obj.fetch_all_email_accounts()
        tran_obj.end()
        return email_accounts
