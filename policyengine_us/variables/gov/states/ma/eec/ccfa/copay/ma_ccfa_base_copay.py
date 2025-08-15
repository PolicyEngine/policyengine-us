from policyengine_us.model_api import *


class ma_ccfa_base_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Massachusetts Child Care Financial Assistance (CCFA) parent base copay"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay

        # Step 1: Get the family's fee level
        fee_level = spm_unit("ma_ccfa_fee_level", period)

        # Step 2: Get the fee percentage for that level
        fee_percentage = p.fee_percentages[fee_level]

        # Step 3: Calculate fee on income above poverty
        income = spm_unit("ma_ccsp_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        income_above_poverty = max_(income - fpg, 0)

        return income_above_poverty * fee_percentage
