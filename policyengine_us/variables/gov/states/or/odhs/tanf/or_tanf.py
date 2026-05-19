from policyengine_us.model_api import *


class or_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://oregon.public.law/rules/oar_461-155-0030",
        "https://oregon.public.law/rules/oar_461-165-0060",
    )
    defined_for = "or_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf
        payment_standard = spm_unit("or_tanf_payment_standard", period)
        adjusted_income = spm_unit("or_tanf_adjusted_income", period)
        calculated_benefit = max_(payment_standard - adjusted_income, 0)
        capped_benefit = min_(calculated_benefit, payment_standard)
        return where(
            capped_benefit >= p.minimum_benefit,
            capped_benefit,
            0,
        )
