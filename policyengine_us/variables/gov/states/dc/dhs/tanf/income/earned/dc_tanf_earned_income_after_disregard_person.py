from policyengine_us.model_api import *


class dc_tanf_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "DC Temporary Assistance for Needy Families (TANF) earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        gross_earnings = person("dc_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.dc.dhs.tanf.income.deductions
        enrolled = person.spm_unit("is_tanf_enrolled", period)
        earnings_after_flat_exclusion = max_(
            gross_earnings - p.work_related_expense.amount, 0
        )
        percentage_disregard = (
            earnings_after_flat_exclusion
            * p.earned_income_disregard.percentage
        )
        return where(
            enrolled,
            # For enrolled recipients, DC applies a flat and a percentage deduction.
            max_(earnings_after_flat_exclusion - percentage_disregard, 0),
            # For new applicants, DC applies only a flat deduction.
            earnings_after_flat_exclusion,
        )
