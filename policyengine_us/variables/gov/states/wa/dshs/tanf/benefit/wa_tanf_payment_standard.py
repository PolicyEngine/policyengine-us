from policyengine_us.model_api import *


class wa_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0020"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.dshs.tanf
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.maximum_family_size)
        return p.payment_standard.amount[size_capped]
