PROJECT_PATH_PREFIX = '/host/hf/hf_email_app/'

AUTH_FOLDER = PROJECT_PATH_PREFIX + 'authorized_emails/'

GMAIL_CLIENT_PAYLOAD_HEADERS = ['To', 'From', 'Subject']
GMAIL_CLIENT_HEADER_MAPPING = {'To': 'to', 'From': 'from', 'Subject': 'subject'}