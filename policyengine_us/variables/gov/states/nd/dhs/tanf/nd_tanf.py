from policyengine_us.model_api import *


class nd_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota Temporary Assistance for Needy Families"
    unit = USD
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_20.htm"
    defined_for = "nd_tanf_eligible"

    def formula(spm_unit, period, parameters):
        standard_of_need = spm_unit("nd_tanf_standard_of_need", period)
        countable_income = spm_unit("nd_tanf_countable_income", period)
        return max_(standard_of_need - countable_income, 0)
