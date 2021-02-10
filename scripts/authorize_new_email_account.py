import sys

from lib.config.custom_logger import get_logger
from middleware.email_manager import EmailManager


LOG = get_logger(__name__)


def authorize_email(email_address, email_client):
    email_manager_obj = EmailManager(email_address, email_client)
    email_manager_obj.authorize_new_email()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        LOG.error("Invalid format. Format expected: python authorize_new_email_account.py abc@gmail.com gmail")
    else:
        authorize_email(sys.argv[1], sys.argv[2])
