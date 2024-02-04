from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = Person
    label = "Mississippi adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=14",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 66
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.tax.income
        gross_income = add(person, period, p.income_sources)
        adjustments = person("ms_agi_adjustments", period)
        net_income = max_(gross_income - adjustments, 0)
        # Allocate income from dependents to tax unit head.
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_net_income = person.tax_unit.sum(is_dependent * net_income)
        is_head = person("is_tax_unit_head", period)
        return ~is_dependent * net_income + is_head * sum_dep_net_income
