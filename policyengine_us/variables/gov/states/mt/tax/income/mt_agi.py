from policyengine_us.model_api import *


class mt_agi(Variable):
    value_type = float
    entity = Person
    label = "Montana Adjusted Gross Income for each individual"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        additions = person("mt_additions", period)
        subtractions = person("mt_subtractions", period)
        mt_agi = max_(agi + additions - subtractions, 0)
        # allocate any dependent net_income to tax unit head
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_net_income = person.tax_unit.sum(is_dependent * mt_agi)
        is_head = person("is_tax_unit_head", period)
        return ~is_dependent * mt_agi + is_head * sum_dep_net_income
