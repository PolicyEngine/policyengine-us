from policyengine_us.model_api import *


class ut_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit"
    unit = USD
    documentation = "Form TC-40, line 20"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html?v=C59-10-S1018_2023050320230503"

    def formula(tax_unit, period, parameters):
        initial_credit = tax_unit("ut_taxpayer_credit_max", period)
        reduction = tax_unit("ut_taxpayer_credit_reduction", period)
        return max_(initial_credit - reduction, 0)
