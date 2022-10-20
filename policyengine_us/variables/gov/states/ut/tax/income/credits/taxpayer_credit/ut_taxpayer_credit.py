from policyengine_us.model_api import *


class ut_taxpayer_credit(Variable):
    """
    The Utah taxpayer tax credit (line 20 on 2021 TC-40 form) is the initial
    credit before phaseout (line 16) minus the phase-out amount (line 19).
    """

    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        ut_taxpayer_credit_max = tax_unit("ut_taxpayer_credit_max", period)
        ut_taxpayer_credit_reduction = tax_unit(
            "ut_taxpayer_credit_reduction", period
        )
        return ut_taxpayer_credit_max - ut_taxpayer_credit_reduction
