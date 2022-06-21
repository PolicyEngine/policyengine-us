from openfisca_us.model_api import *


class ut_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ut_taxpayer_credit_max = tax_unit("ut_taxpayer_credit_max", period)
        ut_taxpayer_credit_reduction = tax_unit(
            "ut_taxpayer_credit_reduction", period
        )
        return ut_taxpayer_credit_max - ut_taxpayer_credit_reduction
