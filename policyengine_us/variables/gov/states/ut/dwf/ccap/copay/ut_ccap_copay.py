from policyengine_us.model_api import *


class ut_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Utah CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/Infosource/eligibilitymanual/Tables,_Appendicies,_and_Charts/Tables,_Appendicies,_and_Charts/Table_4_-_Child_Care_Income_Eligibility_and_Co-Payment.htm",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-707",
    )

    def formula(spm_unit, period, parameters):
        # The co-payment is a sliding scale by household size, countable
        # income group, and the number of children receiving the subsidy
        # (R986-700-707). This variable is not gated on ut_ccap_eligible
        # because the eligibility test itself compares the co-payment to the
        # cost of care.
        p = parameters(period).gov.states.ut.dwf.ccap.copay
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, p.min_household_size, p.max_household_size)
        # ut_ccap_income_group is masked to 0 outside Utah while this formula
        # still runs for the whole population, so floor the lookup key at
        # group 1 to keep it a valid table key.
        income_group = max_(spm_unit("ut_ccap_income_group", period), 1)
        child_count_group = spm_unit("ut_ccap_child_count_group", period)
        return p.amount[capped_size][income_group][child_count_group]
