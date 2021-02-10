import sys

from lib.config.custom_logger import get_logger
from middleware.rule_filter_manager import RuleFilterManager

LOG = get_logger(__name__)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        RuleFilterManager().add_new_rule(sys.argv[1])
    else:
        LOG.error("Invalid format. Format expected: python add_new_filter.py /host/hf_email_app/filter_rules/rule1.json")