from policyengine_us.model_api import *


class ok_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-33"
    )
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        # Per OAC 340:10-3-33(b): Dependent care expenses may be deducted
        # up to $200/month for dependents under age 2
        # up to $175/month for dependents age 2 and older
        p = parameters(period).gov.states.ok.dhs.tanf.income
        person = spm_unit.members

        # Get dependent status and age in years
        dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)  # Returns true age in years

        # Calculate maximum deduction per dependent based on age
        max_deduction_per_dependent = p.deductions.dependent_care.calc(age)
        total_max_deduction = spm_unit.sum(
            max_deduction_per_dependent * dependent
        )

        # Cap at actual childcare expenses.
        childcare_expenses = spm_unit("childcare_expenses", period)

        return min_(childcare_expenses, total_max_deduction)
