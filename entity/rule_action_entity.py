from entity import validation_config
import validictory

class RuleActionEntity(object):
    """
    @summary: The entity class which holds the action values of a given rule.
    """

    def __init__(self, field_name, action, value):
        self._field_name = field_name
        self._action = action
        self._value = value

    @property
    def field_name(self):
        return self._field_name

    @field_name.setter
    def field_name(self, field_name):
        validictory.validate(field_name, validation_config.actions_field)
        self._field_name = field_name

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        validictory.validate(action, validation_config.actions_action)
        self._action = action

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        validictory.validate(value, validation_config.actions_value)
        self._value = value
