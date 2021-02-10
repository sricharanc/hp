from middleware.strategy.gmail_strategy import GmailStrategy

class EmailClientMapperFactory(object):
    """
    @summary: This class provides the mapping for each email client and its respective EmailClient class.
    """

    def __init__(self):
        self.strategy_map = {'gmail': GmailStrategy}

    def get_email_strategy(self, email_client_name):
        """
        @summary: Provides the class of the given email_client_name.
        """
        return self.strategy_map[email_client_name]