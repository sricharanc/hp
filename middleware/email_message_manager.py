from models.email_dao import EmailDao
from entity.email_message import EmailMessage
from entity.email_message_component import EmailMessageComponent

class EmailMessageManager(object):
    """
    @summary: This class provides functionalities to create a given email message.
    """

    def __init__(self, email_account_messages_id, db_obj):
        self.email_account_messages_id = email_account_messages_id
        self.db_obj = db_obj
 
    def get_email_message_object(self):
        """
        @summary: This class fetches the values from the tables for the given email message id and forms the EmailMessage entity.
        @return: an instance of EmailMessage
        """
        email_dao = EmailDao(self.db_obj)

        email_message_dict = email_dao.get_email_account_message(self.email_account_messages_id)
        email_message_obj = self._construct_email_message(email_message_dict)

        email_components = email_dao.get_email_components(self.email_account_messages_id)
        self._construct_email_components(email_message_obj, email_components)

        email_body_component = email_dao.get_email_message_body(self.email_account_messages_id)
        self._construct_email_body(email_message_obj, email_body_component)

        return email_message_obj

    def _construct_email_message(self, email_message_dict):
        email_message_obj = EmailMessage()
        email_message_obj.email_account_messages_id = self.email_account_messages_id
        email_message_obj.email_account_id = email_message_dict['email_account_id']
        email_message_obj.email_client_message_id = email_message_dict['email_client_message_id']
        email_message_obj.email_datetime = email_message_dict['email_datetime']
        return email_message_obj

    def _construct_email_components(self, email_message_obj, email_components):
        for component in email_components:
            component_obj = EmailMessageComponent()
            component_obj.email_account_messages_id = self.email_account_messages_id
            component_obj.component_type = component['component_type']
            component_obj.component_value = component['component_value']
            email_message_obj.components[component['component_type']] = component_obj

    def _construct_email_body(self, email_message_obj, email_body_component):
        component_obj = EmailMessageComponent()
        component_obj.email_account_messages_id = self.email_account_messages_id
        component_obj.component_type = 'body'
        component_obj.component_value = email_body_component['email_message']
        email_message_obj.components['body'] = component_obj
