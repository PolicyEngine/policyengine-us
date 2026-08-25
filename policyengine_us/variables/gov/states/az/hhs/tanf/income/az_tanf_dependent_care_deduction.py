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
        p = parameters(period).gov.states.az.hhs.tanf.income.deductions.care_expenses

        person = spm_unit.members
        age = person("age", period.this_year)

        # Per ARS 46-292, the disregard covers the actual amount billed for
        # the care of an adult or child dependent household member.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])

        # Calculate eligible deduction for dependents (based on age)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        dependent_amount = p.amounts.calc(age) * is_dependent

        # Total eligible deduction
        total_eligible = spm_unit.sum(dependent_amount)

        # Deduction is capped at actual care expenses
        return min_(childcare_expenses + adult_care_expenses, total_eligible)
