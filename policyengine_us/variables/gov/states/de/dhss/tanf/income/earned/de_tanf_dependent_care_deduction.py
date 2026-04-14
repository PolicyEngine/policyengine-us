from policyengine_us.model_api import *


class de_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://help.workworldapp.com/wwwebhelp/de_earned_income_disregards_tanf_and_ga.htm",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: Dependent care up to $200/month for under age 2,
        # $175/month for age 2 and older
        p = parameters(period).gov.states.de.dhss.tanf.income.deductions

        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)

        # Calculate maximum deduction per dependent based on age
        max_per_dependent = p.dependent_care.calc(age)
        total_max = spm_unit.sum(max_per_dependent * is_dependent)

        # Cap at actual childcare expenses.
        childcare_expenses = spm_unit("childcare_expenses", period)

        return min_(childcare_expenses, total_max)
