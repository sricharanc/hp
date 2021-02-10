import os
import validictory
from validictory.validator import FieldValidationError
import json

from lib.transactional_manager import TransactionalManager
from models.filter_dao import FilterDao
# from middleware.config import RULES_JSON_FOLDER
# from entity.rule_set_entity import RuleSetEntity
# from entity.rule_entity import RuleEntity
# from entity.rule_action_entity import RuleActionEntity
# from middleware.criteria_mapper_factory import CriteriaMapperFactory
from lib.config.custom_logger import get_logger
from middleware.rule_executor import RuleExecutor
from entity import validation_config

LOG = get_logger(__name__)


class RuleFilterManager(object):
    """
    @summary: This method is used to apply the filter rules to the email messages.
    """

    def __init__(self):
        """
        @summary: Constructor of this class and initiates the class attributes for this instance.
        """
        self.db_obj = None
        self.tran_obj = None

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

    def add_new_rule(self, file_path):
        """
        @summary: Adds the new rule from the file_path to the table.
        @param file_path: The path in which the rule json is present.
        """
        LOG.info("Entering %s:%s", RuleFilterManager.__name__, self.add_new_rule.__name__)

        try:
            with open(file_path) as f:
                rule_str = f.read().replace('\r\n', '').replace('\n', '')
        except IOError:
            LOG.exception("Seems the file is not found.")
            return

        rule_dict = json.loads(rule_str)
        try:
            validictory.validate(rule_dict, validation_config.rule_set_schema)
        except FieldValidationError:
            LOG.exception("Given json file is not in proper form.")
            return

        rule_name = file_path.split('/')[-1].replace('.json','')
        try:
            self._create_transaction()
            filter_dao = FilterDao(self.db_obj)
            filter_dao.create_new_filter(rule_name, rule_str)
            self.tran_obj.save()
            LOG.info("new filter information is saved to table.")
        except Exception:
            LOG.exception("Exception occured while saving the rule info.")
        finally:
            self.tran_obj.end()

        LOG.info("Exiting %s:%s", RuleFilterManager.__name__, self.add_new_rule.__name__)

    def apply_filters(self):
        """
        @summary: Applies the filters to the emails where the filters are yet to be applied.
        """
        LOG.info("Entering %s:%s", RuleFilterManager.__name__, self.apply_filters.__name__)

        try:
            self._create_transaction()
            filter_dao = FilterDao(self.db_obj)
            filters_list = filter_dao.get_all_filters()
            self.tran_obj.end()
        except Exception:
            LOG.exception("Exception occurred while fetching the rules.")
            self.tran_obj.end()

        
        for filter_record in filters_list:
            RuleExecutor(filter_record).execute()

        LOG.info("Entering %s:%s", RuleFilterManager.__name__, self.apply_filters.__name__)
