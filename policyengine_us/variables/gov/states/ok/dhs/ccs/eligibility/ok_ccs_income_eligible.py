from policyengine_us.model_api import *


class ok_ccs_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oklahoma Child Care Subsidy income eligible"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://okrules.elaws.us/oac/340:40-7-13",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.income
        countable_income = spm_unit("ok_ccs_countable_income", period)
        # The adjusted monthly income is compared to the Appendix C-4 income
        # threshold for the family size; income above the threshold closes
        # the case (OAC 340:40-7-13).
        size = spm_unit("spm_unit_size", period.this_year)
        return countable_income <= p.limit.calc(size)
