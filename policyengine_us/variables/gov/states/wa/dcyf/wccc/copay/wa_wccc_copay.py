from policyengine_us.model_api import *


class wa_wccc_copay(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington WCCC monthly copayment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0075"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.wccc.copay
        smi_fraction = spm_unit("wa_wccc_smi_fraction", period)
        amount = p.amount.calc(smi_fraction)
        waived = spm_unit("wa_wccc_copay_waived", period)
        return where(waived, 0, amount)
