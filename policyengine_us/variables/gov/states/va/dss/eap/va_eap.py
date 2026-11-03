from policyengine_us.model_api import *


class va_eap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Virginia EAP fuel assistance"
    documentation = (
        "Annual Virginia Energy Assistance Program fuel assistance (regular "
        "heating) benefit: the household's benefit points times the statewide "
        "value per point. For period 2026 (FFY2026) the value per point is the "
        "latest published value, $4.531665 for FFY2025, because VDSS reports "
        "each season's value only after the December calculation. The primary "
        "fuel and energy burden points are PolicyEngine placeholders (10 and "
        "13 points). No minimum, maximum or cap at heating charges is applied; "
        "the March 31 vendor-payment limit is not modeled. Eligibility and the "
        "published point tables are verified for FFY2026; earlier years use "
        "parameter backfilling and are unverified historical estimates. Crisis, "
        "cooling, weatherization and equipment assistance are excluded."
    )
    reference = (
        "https://law.lis.virginia.gov/admincode/title22/agency40/chapter680/section30/",
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=9",
        # PDF pages 52-53
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=52",
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/VA_BenefitMatrix_2026.pdf#page=6",
    )
    defined_for = "va_eap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.benefit
        # 22VAC40-680-30(4): "The household's benefit amount will be calculated
        # by multiplying the household's point total by the value per point."
        return spm_unit("va_eap_points", period) * p.value_per_point
