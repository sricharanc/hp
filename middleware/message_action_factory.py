from entity.message_action_mark import MessageActionMark
from entity.message_action_move import MessageActionMove

class MessageActionFactory(object):

    def __init__(self):
        self.strategy_map = {'move': MessageActionMove,
                             'mark': MessageActionMark}

    def get_action_class(self, action_name):
        return self.strategy_map[action_name]