class EmailMessageComponent(object):
    """
    @summary: Entity class to store the individual email message component such as from,to,body of the email message.
    """

    def __init__(self):
        self.email_account_messages_id = None
        self.component_type = None
        self.component_value = None