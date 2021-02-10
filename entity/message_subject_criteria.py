from entity.message_criteria import MessageCriteria

class MessageSubjectCriteria(MessageCriteria):
    """
    @summary: Entity class which extends from MessageCriteria and implements the method to perform the subject filter
    over the email message.
    """

    def applyCriteria(self, email_message_obj, rule_obj):
        self.email_message_obj = email_message_obj
        data = self.email_message_obj.components['subject'].component_value
        criteria_method = self.getCriteriaMethod(rule_obj.predicate)
        return criteria_method(data, rule_obj.value)