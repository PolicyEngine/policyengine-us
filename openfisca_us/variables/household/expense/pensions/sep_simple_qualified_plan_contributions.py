from openfisca_us.model_api import *


class sep_simple_qualified_plan_contributions(Variable):
    value_type = float
    entity = Person
    label = "SEP, SIMPLE or Qualified plan contributions"
    unit = USD
    definition_period = YEAR
