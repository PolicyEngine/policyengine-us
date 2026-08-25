from policyengine_us.model_api import *


class ut_ccap_income_group(Variable):
    value_type = int
    entity = SPMUnit
    label = "Utah CCAP copayment income group"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/Infosource/eligibilitymanual/Tables,_Appendicies,_and_Charts/Tables,_Appendicies,_and_Charts/Table_4_-_Child_Care_Income_Eligibility_and_Co-Payment.htm",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-707",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.copay
        countable_income = spm_unit("ut_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, p.min_household_size, p.max_household_size)
        limits = p.income_limits[capped_size]
        size_node = next(iter(p.income_limits._children.values()))
        group_count = len(size_node._children)
        # Income at or below a group's published upper bound falls in that
        # group; income above the bound falls in the next group. Income above
        # the group 16 bound stays in group 16 (the 85% state median income
        # eligibility ceiling is applied separately in
        # ut_ccap_income_eligible).
        group = np.ones_like(size)
        for upper_group in range(1, group_count):
            upper_bound = limits[np.full_like(capped_size, upper_group)]
            group = group + (countable_income > upper_bound).astype(int)
        return group
