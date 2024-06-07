from policyengine_us.model_api import *


class ny_ctc_additional_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the NY CTC additional credit"
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=5"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        pre_reduction_base_credit = tax_unit("ny_ctc_pre_reduction_base_credit", period)
        base_credit = tax_unit("ny_ctc_base_credit", period)
        return pre_reduction_base_credit > base_credit
