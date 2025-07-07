from policyengine_us.model_api import *


class il_aabd_person(Variable):
    value_type = float
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) cash benefit per person"
    unit = USD
    definition_period = MONTH
    defined_for = "il_aabd_eligible_person"

    def formula(person, period, parameters):
        total_needs = person("il_aabd_need_standard_person", period)
        countable_income = person("il_aabd_countable_income", period)
        return max_(total_needs - countable_income, 0)
