from policyengine_us.model_api import *


class nd_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for North Dakota TANF due to income"
    definition_period = MONTH
    reference = (
        "https://www.hhs.nd.gov/news/hhs-announces-tanf-modernization-effort-aimed-increasing-accessibility-resources-during",
        "https://nd.gov/dhs/policymanuals/40019/Archive%20Documents/2023%20-%20ML%203749/400_19_110_20.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.income.eligibility
        # Per 400-19-110-15: Countable income must be less than
        # the Total Standard of Need (50% FPL as of August 2023)
        countable_income = spm_unit("nd_tanf_countable_income", period)
        standard_of_need = spm_unit("nd_tanf_standard_of_need", period)
        return countable_income < standard_of_need
