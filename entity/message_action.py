from abc import ABC, abstractmethod

class MessageAction(ABC):
    """
    @summary: Abstract Entity class which provides the interface for other action classes.
    """

    @abstractmethod
    def applyAction(self, email_message_obj, action_obj, email_strategy_obj):
        pass
