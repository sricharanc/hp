import sys

from lib.config.custom_logger import get_logger
from middleware.email_manager import BulkEmailManager, EmailManager

LOG = get_logger(__name__)

if __name__ == '__main__':
    command_line_arguments = sys.argv
    if len(command_line_arguments) < 2 or command_line_arguments[1] not in ('all_emails', 'specific_email'):
        LOG.error("Invalid format. Format expected: python fetch_emails.py all_emails or python fetch_emails.py specific_email abc@gmail.com gmail")
    elif command_line_arguments[1] == 'all_emails':
        LOG.info("Emails to be fetched for all email accounts.")
        BulkEmailManager().process_message_download_all_emails()
    elif command_line_arguments[1] == 'specific_email' and len(command_line_arguments) == 4:
        LOG.info("Emails to be fetched for %s", command_line_arguments[2])
        EmailManager(command_line_arguments[2], command_line_arguments[3]).process_message_download()
    else:
        LOG.error("Invalid format. Format expected: python fetch_emails.py all_emails or python fetch_emails.py specific_email abc@gmail.com gmail")
