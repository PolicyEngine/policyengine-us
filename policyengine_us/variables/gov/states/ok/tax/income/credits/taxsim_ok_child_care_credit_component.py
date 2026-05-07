from policyengine_us.model_api import *


class taxsim_ok_child_care_credit_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma child care credit component"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # OK's combined credit is max(CDCC_portion, CTC_portion).
        # This extracts the CDCC portion: combined minus CTC component.
        combined = tax_unit("ok_child_care_child_tax_credit", period)
        ctc = tax_unit("taxsim_ok_child_tax_credit_component", period)
        return max_(0, combined - ctc)
