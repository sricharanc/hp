from entity import validation_config
import validictory

class EmailAccount(object):
    """
    @summary: Entity class to store the Email account information.
    """

    def __init__(self, email_address, email_client_id):
        self._email_address = email_address
        self._email_client_id = email_client_id

    @property
    def email_address(self):
        return self._email_address

    @email_address.setter
    def email_address(self, email_address):
        validictory.validate(email_address, validation_config.email_address)
        self._email_address = email_address

    @property
    def email_client_id(self):
        return self._email_client_id

    @email_client_id.setter
    def email_client_id(self, email_client_id):
        validictory.validate(email_client_id, validation_config.email_client_id)
        self._email_client_id = email_client_id
