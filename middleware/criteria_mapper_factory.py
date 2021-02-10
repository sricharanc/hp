from entity.message_fromaddress_criteria import MessageFromAddressCriteria
from entity.message_toaddress_criteria import MessageToAddressCriteria
from entity.message_subject_criteria import MessageSubjectCriteria
from entity.message_body_criteria import MessageBodyCriteria
from entity.message_datetime_criteria import MessageDatetimeCriteria

class CriteriaMapperFactory(object):
    """
    @summary: This class provides the mapping for each criteria and its respective Criteria class.
    """

    def __init__(self):
        self.strategy_map = {'from': MessageFromAddressCriteria,
                             'to': MessageToAddressCriteria,
                             'subject': MessageSubjectCriteria,
                             'body': MessageBodyCriteria,
                             'date_received': MessageDatetimeCriteria}

    def get_filter_class(self, filter_field_name):
        """
        @summary: Provides the class of the given filter_field_name.
        """
        return self.strategy_map[filter_field_name]