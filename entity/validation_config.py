import re

email_pattern = "^[a-zA-Z0-9]+([\-\.\_+]*[\w])*\@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,4}[\.]?$"

email_address = {"type": "string",
                 'pattern': re.compile(email_pattern, re.IGNORECASE)}

email_client_id = {"type": "integer"}

string_field_names = ["from", "to", "subject", "body", "cc"]
string_field_predicates = ["contains", "do_not_contain", "equals", "not_equal"]

datetime_field_names = ["date_received"]
datetime_field_predicates = ["less_than", "greater_than"]

rule_field_name = {"type": "string", "enum":["from", "to", "subject", "body", "cc", "date_received"]}
rule_predicate = {"type": "string", "enum":["contains", "do_not_contain", "equals", "not_equal", "less_than", "greater_than"]}
rule_value = {"type": "string"}
rule_schema = {"type": "array",
               "required": True,
               "items": {"type": "object",
                         "properties": {"field_name": rule_field_name,
                                        "predicate": rule_predicate,
                                        "value": rule_value
                                        }
                        }
}

actions_field = {"type": "string", "enum":["message"]}
actions_action = {"type": "string", "enum":["move", "mark"]}
actions_value = {"type": "string"}
actions_schema = {"type": "array",
                  "required": True,
                  "items": {"type": "object",
                            "properties": {"field_name": actions_field,
                                           "action": actions_action,
                                           "value": actions_value
                                           }
                            }
                  }

rule_predicate_schema = {"type": "string", "enum": ['all', 'any'], "required": True}

rule_set_schema = {"type": "object",
          "properties": {
                         "rules": rule_schema,
                         "actions": actions_schema,
                         "rule_predicate": rule_predicate_schema,
                         }
          }