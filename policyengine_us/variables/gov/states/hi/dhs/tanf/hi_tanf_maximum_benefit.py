from policyengine_us.model_api import *


class hi_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/",
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf

        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)

        # Get Standard of Need for household size
        son = p.standard_of_need.amount[capped_size]

        # Calculate SOA = SON × 48%
        # Then apply 20% reduction for work-eligible households
        # NOTE: 20% reduction applies after first 2 months of assistance
        # PolicyEngine cannot track months, so reduced rate is used as default
        soa_rate = p.benefit.rate
        reduction_rate = p.benefit.reduction_rate

        return son * soa_rate * (1 - reduction_rate)
