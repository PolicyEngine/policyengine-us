from policyengine_us.model_api import *


class de_agi_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware adjusted gross income for each individual whe married filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        pre_exclusions_agi = person("de_pre_exclusions_agi", period)
        indv_exclusions = person(
            "de_elderly_or_disabled_income_exclusion_joint", period
        )
        net_income = max_(pre_exclusions_agi - indv_exclusions, 0)
        # allocate any dependent gross income to tax unit head
        is_head = person("is_tax_unit_head", period)
        return person.tax_unit.sum(net_income) * is_head
