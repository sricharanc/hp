from abc import ABC, abstractmethod
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MessageCriteria(ABC):
    """
    @summary: This is the base class to serve required features for applying the Criteria of an email message.
    """

    @abstractmethod
    def applyCriteria(self, email_message_obj, rule_obj):
        pass

    def applyContainsCriteria(self, data, value):
        if re.search(value, data, re.IGNORECASE):
            return True
        return False

    def applyDoNotContainsCriteria(self, data, value):
        if not re.search(value, data, re.IGNORECASE):
            return True
        return False

    def applyEqualsCriteria(self, data, value):
        if value.lower() == data.lower():
            return True
        return False

    def applyNotEqualsCriteria(self, data, value):
        if value.lower() != data.lower():
            return True
        return False

    def _get_target_date(self, value):
        value_list = value.split('_')
        d = {'day': 'days', 'month': 'months'}
        date_dict = {d[value_list[1]]: int(value_list[0])*-1}
        target_date = datetime.today() + relativedelta(**date_dict)
        return target_date

    def applyLessThanCriteria(self, data, value):
        if data < self._get_target_date(value):
            return True
        return False

    def applyGreaterThanCriteria(self, data, value):
        if data > self._get_target_date(value):
            return True
        return False

    def getCriteriaMethod(self, predicate):
        predicate_method_dict = {'contains': self.applyContainsCriteria,
                                 'do_not_contain': self.applyDoNotContainsCriteria,
                                 'equals': self.applyEqualsCriteria,
                                 'not_equal': self.applyNotEqualsCriteria,
                                 'less_than': self.applyLessThanCriteria,
                                 'greater_than': self.applyGreaterThanCriteria}
        return predicate_method_dict[predicate]