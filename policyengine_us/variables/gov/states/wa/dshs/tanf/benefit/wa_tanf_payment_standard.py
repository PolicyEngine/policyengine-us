from policyengine_us.model_api import *


class wa_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0020",)
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.wa.dshs.tanf
        payment_standards = p.benefit.payment_standard
        max_family_size = p.maximum_family_size

        # Get household size, capped at maximum for which standards are defined
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, max_family_size)

        # Get payment standard for this family size
        payment_standard = payment_standards[size_capped]

        return payment_standard
