from policyengine_us.model_api import *


class pell_grant_head_contribution(Variable):
    value_type = float
    entity = Person
    label = "Head Contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        available_income = person("pell_grant_head_available_income", period)
        dependents = person("pell_grant_dependents_in_college", period)
        formula = person("pell_grant_formula", period).decode_to_str()
        p = parameters(period).gov.ed.pell_grant.efc.head
        base = p.base.calc(available_income)
        additional = p.percent.calc(available_income)
        threshold = p.threshold.calc(available_income)
        total_head_contribution = base + (
            (available_income - threshold) * additional
        )
        return where(
            formula == "B",
            available_income / dependents,
            total_head_contribution / dependents,
        )
