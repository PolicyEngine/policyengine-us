from policyengine_us.model_api import *


class nv_ccdp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Nevada CCDP monthly family co-payment"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Care/CC%20PT%2006-25%20ANNUAL%20INCOME%20CHANGES%2010.02.2025.pdf#page=1"

    def formula(spm_unit, period, parameters):
        # CC PT 06-25 (eff. Oct 1, 2025) replaced the manual's old sliding
        # scale with a flat monthly copay keyed by income as a share of SMI:
        # <= 32.99% SMI -> $0; 33%-42% SMI -> $90; 43%-49% SMI -> $150.
        p = parameters(period).gov.states.nv.dwss.ccdp.copay
        # Floor income at 0 before taking the ratio: negative self-employment
        # income would otherwise produce a negative ratio and the wrong band.
        monthly_income = max_(
            spm_unit("nv_ccdp_countable_income", period.this_year) / MONTHS_IN_YEAR,
            0,
        )
        monthly_smi = spm_unit("nv_ccdp_smi", period)
        smi_ratio = where(monthly_smi > 0, monthly_income / monthly_smi, 0)
        copay = p.amount.calc(smi_ratio)
        # MS 163 / CCDF Plan Section 3.3.1: copay waived for TANF/NEON
        # referrals, CPS/foster placements, and homeless households. Use
        # is_tanf_enrolled for the NEON waiver to avoid the CCDP <-> TANF
        # circular dependency. Waivers apply at the whole-family level; we
        # don't track per-child copay waivers at the moment.
        # State Plan Section 3.3.1 additionally lists copay waivers for
        # children with disabilities and for Head Start / Early Head Start
        # enrollees, which we don't track at the moment: the operative
        # Manual MS 163 omits both categories.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        is_eligible_child = person("nv_ccdp_eligible_child", period)
        in_protective_care = is_eligible_child & (
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        has_protective_child = spm_unit.any(in_protective_care)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        waived = is_tanf_enrolled | has_protective_child | is_homeless
        return where(waived, 0, copay)
