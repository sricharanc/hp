from entity import validation_config
import validictory

class RuleSetEntity(object):
    """
    @summary: The entity class which holds the entire rule with individual rules and its actions.
    """

    def __init__(self):
        self.rules = []
        self.actions = []
        self.rule_predicate = None
