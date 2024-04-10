from policyengine_us.model_api import *


class de_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = "Delaware adjusted gross income for each individual when married filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        pre_exclusions_agi = person("de_pre_exclusions_agi", period)
        indv_exclusions = person(
            "de_elderly_or_disabled_income_exclusion_indiv", period
        )
        net_income = max_(pre_exclusions_agi - indv_exclusions, 0)
        # allocate any dependent gross income to tax unit head
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_net_income = person.tax_unit.sum(is_dependent * net_income)
        is_head = person("is_tax_unit_head", period)
        head_spouse_net_income = ~is_dependent * net_income
        head_allocated_dependent_net_income = is_head * sum_dep_net_income
        return head_spouse_net_income + head_allocated_dependent_net_income
