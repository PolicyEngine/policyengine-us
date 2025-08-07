from policyengine_us.model_api import *


class pell_grant_head_available_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant head available income"
    definition_period = YEAR

    def formula(person, period, parameters):
        allowances = person("pell_grant_head_allowances", period)
        income = person.tax_unit("pell_grant_primary_income", period)
        formula = person("pell_grant_formula", period)
        p = parameters(period).gov.ed.pell_grant.head
        return (income - allowances) * p.income_assessment_rate[formula]
