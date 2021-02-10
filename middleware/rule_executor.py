import json

from lib.config.custom_logger import get_logger
from lib.transactional_manager import TransactionalManager
from models.email_dao import EmailDao
from models.filter_dao import FilterDao
from entity.rule_set_entity import RuleSetEntity
from entity.rule_entity import RuleEntity
from entity.rule_action_entity import RuleActionEntity
from middleware.email_message_manager import EmailMessageManager
from middleware.criteria_mapper_factory import CriteriaMapperFactory
from middleware.message_action_factory import MessageActionFactory
from middleware.email_client_mapper_factory import EmailClientMapperFactory

LOG = get_logger(__name__)

class RuleExecutor(object):
    """
    @summary: This class executes the filter rule for a set of messages.
    """

    def __init__(self, filter_dict):
        self.filter_data = filter_dict
        self.tran_obj = None
        self.db_obj = None

    def _create_transaction(self):
        """
        @summary: Creates a new transaction object in order to perform the required db operations.
        @return: None
        """
        try:
            if not self.tran_obj:
                LOG.info("Creating transaction.")
                self.tran_obj = TransactionalManager()
                self.db_obj = self.tran_obj.get_database_connection()
        except Exception as e:
            LOG.error("Exception while creating a transaction: %s", e)
            raise

    def _get_ruleset_object(self):
        """
        @summary: Forms the ruleset object and returns it.
        @return: An instance of Ruleset class
        """
        rule_dict = json.loads(self.filter_data['rule_value'])
        rule_set_obj = RuleSetEntity()
        for individual_rule in rule_dict['rules']:
            rule_obj = RuleEntity(individual_rule['field_name'], individual_rule['predicate'], individual_rule['value'])
            rule_set_obj.rules.append(rule_obj)
        for individual_action in rule_dict['actions']:
            action_obj = RuleActionEntity(individual_action['field_name'], individual_action['action'], individual_action['value'])
            rule_set_obj.actions.append(action_obj)
        rule_set_obj.rule_predicate = rule_dict['rule_predicate']
        return rule_set_obj

    def _get_email_message_object(self, email_account_messages_id):
        return EmailMessageManager(email_account_messages_id, self.db_obj).get_email_message_object()

    def execute(self):
        """
        @summary: This method applies the rule to the messages for which the rule is yet to be applied.
        """
        LOG.info("Entering %s:%s", RuleExecutor.__name__, self.execute.__name__)

        rule_set_obj = self._get_ruleset_object()
        LOG.info("Ruleset object created.")

        try:
            self._create_transaction()
            filter_dao = FilterDao(self.db_obj)
            eligible_messages = filter_dao.get_eligible_emails_for_filtering(self.filter_data['filter_rules_id'])
            for email_account_messages_id in eligible_messages:
                email_message_obj = self._get_email_message_object(email_account_messages_id['email_account_messages_id'])
                self.apply_rule(rule_set_obj, email_message_obj)
                self.tran_obj.save()
                self.tran_obj.end()
        except Exception:
            LOG.exception('Error while applying the rules to the message.')
            if self.tran_obj:
                self.tran_obj.revertback()
                self.tran_obj.end()

        LOG.info("Exiting %s:%s", RuleExecutor.__name__, self.execute.__name__)

    def apply_rule(self, rule_set_obj, email_message_obj):
        """
        @summary: This method applies the given rule to the given email message.
        @param rule_set_obj: Instance of RuleSet
        @param email_message_obj: Instance of Email Message to which the rule is to be applied
        """
        if self._is_rule_applicable(rule_set_obj, email_message_obj):
            self._perform_action(rule_set_obj, email_message_obj)
        filter_dao = FilterDao(self.db_obj)
        filter_dao.create_email_message_filter_rules_status(email_message_obj.email_account_messages_id,
                                                            self.filter_data['filter_rules_id'])

    def _is_rule_applicable(self, rule_set_obj, email_message_obj):
        """
        @summary: Checks whether the rules is appllicable for the email message or not.
        @param rule_set_obj: Instance of RuleSet
        @param email_message_obj: Instance of Email Message to which the rule is to be applied
        @return: Boolean - indicates whether a rule is applicable or not.
        """
        criteria_factory_obj = CriteriaMapperFactory()
        rule_applicable = None

        for rule_obj in rule_set_obj.rules:
            filter_class = criteria_factory_obj.get_filter_class(rule_obj.field_name)
            filter_obj = filter_class()
            result = filter_obj.applyCriteria(email_message_obj, rule_obj)
            if rule_set_obj.rule_predicate == 'all' and not result:
                rule_applicable = False
                break
            elif rule_set_obj.rule_predicate == 'any' and result:
                rule_applicable = True
                break
        if rule_set_obj.rule_predicate == 'all' and rule_applicable != False:
            rule_applicable = True
        return rule_applicable

    def _perform_action(self, rule_set_obj, email_message_obj):
        """
        @summary: This method will enable us to perform the rule action over the email.
        @param rule_set_obj: Instance of RuleSet
        @param email_message_obj: Instance of Email Message to which the action is to be applied
        """
        email_dao = EmailDao(self.db_obj)
        email_mess_dict = email_dao.get_email_account_with_email_account_id(email_message_obj.email_account_id)

        email_strategy_obj = self._get_email_strategy_obj(email_mess_dict)
        action_factory_obj = MessageActionFactory()

        for action_obj in rule_set_obj.actions:
            action_class = action_factory_obj.get_action_class(action_obj.action)
            message_action_obj = action_class()
            message_action_obj.applyAction(email_message_obj, action_obj, email_strategy_obj)

    def _get_email_strategy_obj(self, email_mess_dict):
        """
        @summary: This method will connect with EmailClientMapperFactory and returns the EmailStrategy object.
        @return: An instance of the associated EmailStrategy.
        """
        factory_obj = EmailClientMapperFactory()
        strategy = factory_obj.get_email_strategy(email_mess_dict['email_client'])
        return strategy(self.db_obj, self.tran_obj, email_mess_dict['email_address'])
