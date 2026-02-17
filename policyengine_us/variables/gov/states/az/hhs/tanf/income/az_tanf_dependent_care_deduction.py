from policyengine_us.model_api import *


class az_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00292.htm"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.income.deductions.care_expenses

        person = spm_unit.members
        age = person("age", period.this_year)

        childcare_expenses = spm_unit("childcare_expenses", period)

        # Calculate eligible deduction for dependent children (based on age)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        child_amount = p.amounts.calc(age) * is_dependent

        # Total eligible deduction
        total_eligible = spm_unit.sum(child_amount)

        # Deduction is capped at actual childcare expenses
        return min_(childcare_expenses, total_eligible)
