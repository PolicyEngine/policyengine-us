from policyengine_us.model_api import *


class taxsim_ok_child_tax_credit_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma child tax credit component"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # OK's combined credit is max(CDCC_portion, CTC_portion).
        # This extracts the CTC portion by checking if CTC > CDCC.
        p = parameters(period).gov.states.ok.tax.income.credits.child
        us_cdcc = tax_unit("cdcc_potential", period)
        ok_cdcc = us_cdcc * p.cdcc_fraction
        us_ctc = tax_unit("ctc_value", period)
        ok_ctc = us_ctc * p.ctc_fraction
        ctc_larger_than_cdcc = ok_ctc > ok_cdcc
        combined = tax_unit("ok_child_care_child_tax_credit", period)
        return where(ctc_larger_than_cdcc, combined, 0)
