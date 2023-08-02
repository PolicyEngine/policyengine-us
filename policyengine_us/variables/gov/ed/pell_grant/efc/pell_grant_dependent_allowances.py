from policyengine_us.model_api import *


class pell_grant_dependent_allowances(Variable):
    value_type = float
    entity = Person
    label = "Dependent Allowances"
    definition_period = YEAR

    def formula(person, period, parameters):
        other_allowances = person("pell_grant_dependent_other_allowances", period)
        ipa = parameters(period).gov.ed.pell_grant.efc.dependent.ipa
        head_available_income = person("pell_grant_head_available_income", period)
        allowances_from_head = where(head_available_income < 0, -head_available_income, 0)
        return ipa + allowances_from_head + other_allowances
