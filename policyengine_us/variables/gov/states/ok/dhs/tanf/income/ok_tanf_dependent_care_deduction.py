from policyengine_us.model_api import *


class ok_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-33"
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        # Per OAC 340:10-3-33(b)(3): Dependent care expenses may be deducted
        # up to $200/month for dependents under age 2
        # up to $175/month for dependents age 2 and older or for an
        # incapacitated adult included in the TANF assistance unit
        p = parameters(period).gov.states.ok.dhs.tanf.income
        person = spm_unit.members

        # Get dependent status and age in years
        dependent = person("is_tax_unit_dependent", period)
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("monthly_age", period)  # Returns true age in years

        # Calculate maximum deduction per care recipient based on age
        care_recipient = dependent | incapacitated_adult
        max_deduction_per_person = p.deductions.dependent_care.calc(age)
        total_max_deduction = spm_unit.sum(max_deduction_per_person * care_recipient)

        # Cap at actual care expenses.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])

        return min_(childcare_expenses + adult_care_expenses, total_max_deduction)
