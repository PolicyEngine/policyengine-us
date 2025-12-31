from policyengine_us.model_api import *


class nd_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota Temporary Assistance for Needy Families"
    unit = USD
    definition_period = MONTH
    reference = "https://nd.gov/dhs/policymanuals/40019/Archive%20Documents/2023%20-%20ML%203749/400_19_110_20.htm"
    defined_for = "nd_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.benefit
        # Per 400-19-110-20: Benefit = Standard of Need - Countable Income
        standard_of_need = spm_unit("nd_tanf_standard_of_need", period)
        countable_income = spm_unit("nd_tanf_countable_income", period)
        gross_benefit = max_(standard_of_need - countable_income, 0)
        # Per 400-19-110-20: Minimum benefit is $10; if less, no benefit issued
        return where(gross_benefit >= p.minimum, gross_benefit, 0)
