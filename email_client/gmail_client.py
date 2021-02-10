import os.path
import pickle
from datetime import datetime, timezone
from base64 import urlsafe_b64decode

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from email_client.config import AUTH_FOLDER, GMAIL_CLIENT_PAYLOAD_HEADERS, GMAIL_CLIENT_HEADER_MAPPING
from entity.email_message import EmailMessage
from entity.email_message_component import EmailMessageComponent
from lib.config.custom_logger import get_logger

LOG = get_logger(__name__)

class GmailClient(object):
    """
    @summary: This class is the interface between our application and the GMAIL API.
    """

    def __init__(self, email_address):
        """
        @summary: This is the constructor of this class and initializes the required attributes for this class.
        @param email_address: The email_address for which the client operations are to be performed.
        """
        self.service_obj = None
        self.email_address = email_address
        self.pickle_file_path = AUTH_FOLDER + self.email_address + '.pickle'
        self._last_page_token = None
        self.email_account_id = None

    def check_pickle_file(self):
        """
        @summary: Checks whether the required pickle file is present or not and returns the status.
        @return: Boolean
        """
        return os.path.exists(self.pickle_file_path)

    def load_pickle(self):
        """
        @summary: This method loads the pickle file and returns them.
        @return: UnPickled value
        """
        if self.check_pickle_file():
            with open(self.pickle_file_path, 'rb') as token:
                return pickle.load(token)

    def create_authorization(self):
        """
        @summary: Creates the necessary authorization for this email_account by connecting with GMAIL API.
        Saves the authorization pickle file to the authorized_emails folder.
        """
        LOG.info("Entering %s:%s", GmailClient.__name__, self.create_authorization.__name__)

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.labels',
                        'https://www.googleapis.com/auth/gmail.modify']
        creds = self.load_pickle()
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.pickle_file_path, 'wb') as token:
                pickle.dump(creds, token)

        LOG.info("Exiting %s:%s", GmailClient.__name__, self.create_authorization.__name__)

    def connect(self):
        """
        @summary: Connects with the GMAIL API and creates the service obj for this instance.
        """
        creds = self.load_pickle()
        self.service_obj = build('gmail', 'v1', credentials=creds)

    def download_emails(self, email_dao):
        """
        @summary: This will check for new messages from the email inbox and returns the list
        containing the email_account_messages_id.
        @return: list - with the email_account_messages_ids
        """
        LOG.info("Entering %s:%s", GmailClient.__name__, self.download_emails.__name__)

        try:
            self.connect()
            self.email_dao = email_dao
            result = self.email_dao.get_specific_email_account(self.email_address)
            self.email_account_id = result['email_account_id']
            if result['last_update_id']:
                return self._download_emails_from_last_history(result['last_update_id'])
            else:
                return self._download_emails_without_history()
        except Exception:
            LOG.error('Error when downloading email messages.')
            raise

    def _download_emails_without_history(self):
        """
        @summary: This method downloads the email messages without any previous historical information in the tables.
        Also, saves the latest history information to the email account.
        @return: list - with the email_account_messages_ids
        """
        list_args = {'userId': self.email_address, 'maxResults': 1000}
        LOG.info('Fetching emails from gmail...')
        message_list_result = self.service_obj.users().messages().list(**list_args).execute()
        messages = message_list_result['messages']
        messages_created = []
        messages_created.extend(self._create_message(messages))
        while message_list_result.get('nextPageToken'):
            list_args['pageToken'] = message_list_result['nextPageToken']
            LOG.info('Fetching emails from gmail...')
            message_list_result = self.service_obj.users().messages().list(**list_args).execute()
            messages = message_list_result['messages']
            messages_created.extend(self._create_message(messages))
        #Once all messages are downloaded update the last_update_id in email_account.
        LOG.info('Updating the history id to the table.')
        self.email_dao.update_email_account_email_client_message_id(self.email_account_id, self.get_latest_history_id())
        return messages_created

    def _create_message(self, messages_list):
        """
        @summary: This method downloads the given set of messages list and adds them to the table.
        @param messages_list: The list of message_id of gmail which needs to be downloaded later.
        @return: list - with the email_account_messages_ids
        """
        messages_created = []
        for message in messages_list:
            email_message_obj = EmailMessage()
            email_message_obj.email_account_id = self.email_account_id
            email_message_obj.email_client_message_id = message['id']
            email_account_messages_id = self.email_dao.create_email_message(email_message_obj)
            self.email_dao.db_conn.commit()
            messages_created.append(email_account_messages_id)
        return messages_created

    def get_latest_history_id(self):
        """
        @summary: Connects with the gmail api and returns the latest history id of this gmail app.
        @return: str - the history id value
        """
        return self.service_obj.users().getProfile(userId=self.email_address).execute()['historyId']

    def download_all_email_components(self, email_account_messages_id):
        """
        @summary: Downloads the entire email components for the given email_account_messages_id.
        @param email_account_messages_id: The id for which the email is to be downloaded from gmail.
        """
        email_message_dict = self.email_dao.get_email_account_message(email_account_messages_id)
        email_dict = self._get_individual_message(email_message_dict['email_client_message_id'])
        self._process_email_message(email_dict, email_account_messages_id)

    def _get_individual_message(self, message_id):
        """
        @summary: Connects with gmail api and returns the entire message data.
        @return: Dictionary - data containing entire message
        """
        return self.service_obj.users().messages().get(userId=self.email_address, id=message_id, format='full').execute()

    def _process_email_message(self, email_message, email_account_messages_id):
        """
        @summary: processes the given email_message and saves it to the respective tables.
        @param email_message: The email message for which the data is to be saved.
        @param email_account_messages_id: The id to which the components are to be saved.
        """
        email_message_obj = EmailMessage()
        email_message_obj.email_account_id = self.email_account_id
        email_message_obj.email_client_message_id = email_message['id']
        email_message_obj.email_datetime = datetime.fromtimestamp(int(email_message['internalDate'])/1000, timezone.utc)
        self.email_dao.update_email_datetime(email_account_messages_id, email_message_obj.email_datetime)
        email_message_obj.components = self._add_message_component(email_message, email_account_messages_id)
        return email_message_obj

    def _add_message_component(self, email_message, email_account_messages_id):
        """
        @summary: processes the components of the given email_message and saves it to the respective tables.
        @param email_message: The email message for which the data is to be saved.
        @param email_account_messages_id: The id to which the components are to be saved.
        """
        components_dict = {'from': None, 'to': [], 'subject': None}
        message_headers = email_message['payload']['headers']
        for header in message_headers:
            if header['name'] in GMAIL_CLIENT_PAYLOAD_HEADERS:
                email_message_component_obj = EmailMessageComponent()
                email_message_component_obj.email_account_messages_id = email_account_messages_id
                email_message_component_obj.component_type = GMAIL_CLIENT_HEADER_MAPPING[header['name']]
                email_message_component_obj.component_value = header['value']
                self.email_dao.create_email_message_component(email_message_component_obj)
                if email_message_component_obj.component_type == 'to':
                    components_dict[email_message_component_obj.component_type].append(email_message_component_obj)
                else:
                    components_dict[email_message_component_obj.component_type] = email_message_component_obj
        components_dict['body'] = self._add_message_body(email_message, email_account_messages_id)
        return components_dict

    def _add_message_body(self, email_message, email_account_messages_id):
        """
        @summary: processes the body of the given email_message and saves it to the respective tables.
        @param email_message: The email message for which the data is to be saved.
        @param email_account_messages_id: The id to which the body are to be saved.
        """
        if 'parts' in email_message['payload']:
            email_payload = email_message['payload']['parts']
            for payload in email_payload:
                if payload['mimeType'] == 'text/plain':
                    self._add_body(email_account_messages_id, payload['body']['data'])
        else:
            self._add_body(email_account_messages_id, email_message['payload']['body']['data'])

    def _add_body(self, email_account_messages_id, body_data):
        """
        @summary: processes the body of the given email_message and saves it to the respective tables.
        @param email_message: The email message for which the data is to be saved.
        @param email_account_messages_id: The id to which the components are to be saved.
        """
        email_message_component_obj = EmailMessageComponent()
        email_message_component_obj.email_account_messages_id = email_account_messages_id
        email_message_component_obj.component_type = 'body'
        body_data = body_data.replace("-","+").replace("_","/")
        email_message_component_obj.component_value = str(urlsafe_b64decode(body_data.encode('UTF8')))
        self.email_dao.create_email_message_body(email_message_component_obj)
        return email_message_component_obj

    def move_message(self, email_client_message_id, value):
        """
        @summary: This method is used to move the given message to the desired label.
        @param email_client_message_id: The message id for which the operation has to be performed.
        @param value: The target value where the message needs to be moved.
        """
        LOG.info("Entering %s:%s", GmailClient.__name__, self.move_message.__name__)

        self.connect()
        body = {'addLabelIds': [value]}
        self.service_obj.users().messages().modify(userId=self.email_address, id=email_client_message_id, body=body).execute()

        LOG.info("Exiting %s:%s", GmailClient.__name__, self.move_message.__name__)

    def mark_message(self, email_client_message_id, value):
        """
        @summary: This method is used to either mark the message read or unread.
        @param email_client_message_id: The message id for which the operation has to be performed.
        @param value: The target value where the message needs to be moved.
        """
        LOG.info("Entering %s:%s", GmailClient.__name__, self.mark_message.__name__)

        self.connect()
        if value == 'read':
            body = {'removeLabelIds': ['UNREAD']}
        elif value == 'unread':
            body = {'addLabelIds': ['UNREAD']}
        self.service_obj.users().messages().modify(userId=self.email_address, id=email_client_message_id, body=body).execute()

        LOG.info("Exiting %s:%s", GmailClient.__name__, self.mark_message.__name__)
