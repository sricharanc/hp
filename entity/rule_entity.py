from entity import validation_config
import validictory

class RuleEntity(object):
    """
    @summary: The entity class which holds a particular rule.
    """

    def __init__(self, field_name, predicate, value):
        self._field_name = field_name
        self._predicate = predicate
        self._value = value

    @property
    def field_name(self):
        return self._field_name

    @field_name.setter
    def field_name(self, field_name):
        validictory.validate(field_name, validation_config.rule_field_name)
        self._field_name = field_name

    @property
    def predicate(self):
        return self._predicate

    @predicate.setter
    def predicate(self, predicate):
        validictory.validate(predicate, validation_config.rule_predicate)
        self._predicate = predicate

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        validictory.validate(value, validation_config.rule_value)
        self._value = value
