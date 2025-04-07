from policyengine_us.model_api import *


class pell_grant_dependent_allowances(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant dependent allowances"
    definition_period = YEAR

    def formula(person, period, parameters):
        other_allowances = person(
            "pell_grant_dependent_other_allowances", period
        )
        ipa = parameters(period).gov.ed.pell_grant.dependent.ipa
        head_available_income = person(
            "pell_grant_head_available_income", period
        )
        allowances_from_head = -min_(head_available_income, 0)
        return ipa + allowances_from_head + other_allowances
