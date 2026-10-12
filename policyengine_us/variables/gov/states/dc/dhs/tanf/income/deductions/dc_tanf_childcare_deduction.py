from policyengine_us.model_api import *


class dc_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) child care deduction "
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"  # (A)(2)
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.income.deductions.child_care
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        # Per DC Code 4-205.11(a)(2), the deduction covers care of each
        # dependent child or an incapacitated adult living in the same
        # home and receiving TANF or POWER.
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        care_recipient = dependent | incapacitated_adult
        care_deduction_person = p.amount.calc(age) * care_recipient
        total_care_deduction = spm_unit.sum(care_deduction_person)

        return min_(childcare_expenses + adult_care_expenses, total_care_deduction)
