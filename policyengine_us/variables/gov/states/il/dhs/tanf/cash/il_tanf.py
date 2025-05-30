from policyengine_us.model_api import *


class il_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "il_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Illinois-specific TANF calculation
        household_size = spm_unit("spm_unit_size", period).astype(str)
        max_amount = parameters(period).gov.states.il.dhs.tanf.cash.amount.max[
            household_size
        ]
        countable_income = spm_unit("il_tanf_countable_income", period)
        # Convert monthly to annual
        return max_(0, max_amount - countable_income) * MONTHS_IN_YEAR
