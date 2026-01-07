from policyengine_us.model_api import *


class nj_wfnj_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ income eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-1",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3",
    )
    # NOTE: Per N.J.A.C. 10:90-3.8, initial applicants should be tested against
    # gross income without disregards. PolicyEngine cannot distinguish initial
    # vs ongoing recipients, so this applies the ongoing eligibility test to all.
    # The implementation also combines the initial test (income <= max allowable)
    # with the ongoing test (income < max benefit), which is more restrictive
    # than applying only the initial test for new applicants.

    def formula(spm_unit, period, parameters):
        income = spm_unit("nj_wfnj_countable_income", period)
        maximum_allowable_income = spm_unit(
            "nj_wfnj_maximum_allowable_income", period
        )
        maximum_benefit = spm_unit("nj_wfnj_maximum_benefit", period)
        return (income <= maximum_allowable_income) & (
            income < maximum_benefit
        )
