from openfisca_us.model_api import *


class snap_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Earnings deduction for calculating SNAP benefit amount"
    label = "SNAP earnings deduction"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_2"

    def formula(spm_unit, period, parameters):
        deduction_rate = parameters(period).usda.snap.earnings_deduction
        return spm_unit("snap_gross_income", period) * deduction_rate
