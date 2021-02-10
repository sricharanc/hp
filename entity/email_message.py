class EmailMessage(object):
    """
    @summary: Entity class to store the complete email message along with different components.
    """

    def __init__(self):
        self.email_account_id = None
        self.email_client_message_id = None
        self.email_datetime = None
        self.components = {}
        self.email_account_messages_id = None