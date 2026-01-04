from policyengine_us.model_api import *


class nd_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for North Dakota TANF due to income"
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_15.htm"
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("nd_tanf_countable_income", period)
        standard_of_need = spm_unit("nd_tanf_standard_of_need", period)
        return countable_income < standard_of_need
