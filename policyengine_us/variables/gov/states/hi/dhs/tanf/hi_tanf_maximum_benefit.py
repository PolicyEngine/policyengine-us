from policyengine_us.model_api import *


class hi_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=22",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf

        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)

        # Standard of Need (SON) = 100% of 2006 Hawaii FPG.
        son = p.standard_of_need.amount[capped_size]

        # Standard of Assistance (SOA) = SON × the standard-of-assistance
        # rate (48% per HI TANF State Plan 11.1; raised to 62% effective
        # March 1, 2025 per the DHS BESSD § 346-51.5 HRS report).
        soa = son * p.standard_of_assistance.rate

        # Per HI TANF State Plan 11.1 footnote 4: SOA is further reduced by 20%
        # after the family received their initial two full months of benefits
        # and is applicable to mandatory-work-required TANF households,
        # effective July 1, 2009. Households exempt from work requirements
        # and households in their first two months continue to receive the
        # un-reduced SOA. PolicyEngine cannot track cumulative months of
        # benefit receipt, so the steady-state mandatory-work convention is
        # applied by default — this matches the figure reported by CBPP and
        # the Urban Welfare Rules Database for cross-state benefit comparison.
        return soa * (1 - p.standard_of_assistance.mandatory_work_reduction)
