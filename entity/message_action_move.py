from entity.message_action import MessageAction

class MessageActionMove(MessageAction):
    """
    @summary: Entity class which extends from MessageAction and implements the method to perform the move action
    over the email message.
    """

    def applyAction(self, email_message_obj, action_obj, email_strategy_obj):
        email_strategy_obj.move_message(email_message_obj.email_client_message_id,
                                        action_obj.value)