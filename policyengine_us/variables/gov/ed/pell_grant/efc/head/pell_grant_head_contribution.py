from policyengine_us.model_api import *


class pell_grant_head_contribution(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant head contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        available_income = person("pell_grant_head_available_income", period)
        dependents = person.tax_unit(
            "pell_grant_dependents_in_college", period
        )
        formula = person("pell_grant_formula", period).decode_to_str()
        p = parameters(period).gov.ed.pell_grant.efc.head
        positive_head_contribution = p.marginal_rate.calc(available_income)
        negative_head_contribution = max_(
            available_income * p.negative_rate, p.min_contribution
        )
        total_head_contribution = where(
            available_income >= 0,
            positive_head_contribution,
            negative_head_contribution,
        )
        total = where(
            formula == "B", available_income, total_head_contribution
        )
        return total / dependents
