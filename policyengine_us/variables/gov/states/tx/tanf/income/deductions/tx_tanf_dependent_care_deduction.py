from policyengine_us.model_api import *


class tx_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1420-types-deductions",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-409",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Actual cost of dependent child care, capped at maximum by age
        # Per § 372.409 (a)(3): up to $200/month for children under 2, $175/month for children 2+

        # Get actual childcare expenses
        childcare_expenses = spm_unit("childcare_expenses", period)

        # Calculate maximum deduction for dependents (children or incapacitated adults)
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        is_incapacitated = person("is_incapable_of_self_care", period)
        age = person("monthly_age", period)

        # Eligible for deduction: dependent child OR incapacitated adult
        eligible_for_deduction = is_dependent | is_incapacitated

        p = parameters(period).gov.states.tx.tanf.income
        max_per_person = where(
            eligible_for_deduction, p.deductions.dependent_care.calc(age), 0
        )
        total_max_deduction = spm_unit.sum(max_per_person)

        # Deduction is the lesser of actual expenses or maximum
        return min_(childcare_expenses, total_max_deduction)
