from policyengine_us.model_api import *


class pell_grant_parent_contribution(Variable):
    value_type = float
    entity = Person
    label = "Parent Contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person("pell_grant_parent_assets", period)
        allowances = person("pell_grant_parent_allowances", period)
        income = person("pell_grant_parent_income", period)
        students = person("pell_grant_students_in_college", period)
        p = parameters(period).gov.ed.pell_grant.efc.parent
        ajusted_assets = assets * p.asset_modification
        ajusted_income = income - allowances
        available_income = ajusted_income + ajusted_assets
        base = p.base.calc(available_income)
        additional = p.percent.calc(available_income)
        threshold = p.threshold.calc(available_income)
        total_parent_contribution = base + ((available_income - threshold) * additional)
        return total_parent_contribution / students
