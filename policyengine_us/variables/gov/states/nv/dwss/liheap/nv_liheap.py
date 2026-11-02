from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nv_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP Fixed Annual Credit"
    documentation = (
        "Nevada's single regular benefit, the Fixed Annual Credit, paid "
        "toward the household's primary heating and electric energy costs "
        "over the state fiscal year (July-June): the annual energy cost less "
        "the statewide median energy burden share of income, at least the "
        "minimum payment and at most the capped benefit table amount. Model "
        "period 2026 is SFY2026 and 2027 is SFY2027. Verified for SFY2026 and "
        "SFY2027; earlier years are unverified estimates through parameter "
        "backfilling. Crisis assistance (Fast Track), arrearage payments and "
        "weatherization are out of scope."
    )
    defined_for = "nv_liheap_eligible"
    reference = (
        "https://www.leg.state.nv.us/nrs/nrs-702.html#NRS702Sec260",
        # PDF pages 35, 60-61, 104-105, 110-111
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=35",
        # PDF pages 35, 60-61, 103-104, 110-111
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=35",
        "https://liheapch.acf.gov/docs/2026/state-plans/NV_Plan_2026.pdf#page=9",
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/fy-2027-low-income-home-energy-assistance-program-liheap-state-plan.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.liheap
        income = spm_unit("nv_liheap_fac_income", period)
        energy_cost = spm_unit("nv_liheap_energy_cost", period)
        # The credit is the energy cost less the expected payment at the
        # median energy burden. A credit below the minimum, including a
        # negative credit and utilities included in the rent with no bill,
        # pays the minimum.
        fac = energy_cost - income * p.payment.burden_rate
        benefit = max_(fac, p.payment.minimum)
        size = spm_unit("nv_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size,
            state_group,
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        p_cap = p.payment.cap
        band = p_cap.income_band.calc(income / guideline, right=True).astype(int)
        # Eligible households have at least one member; the lower bound only
        # keeps the table lookup defined for other units.
        table_size = clip(size, 1, p_cap.max_household_size)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        propane_or_oil = (
            (heating_type == types.PROPANE)
            | (heating_type == types.FUEL_OIL)
            | (heating_type == types.KEROSENE)
        )
        table_cap = where(
            propane_or_oil,
            p_cap.propane_and_oil[table_size][band],
            p_cap.standard[table_size][band],
        )
        # A counted member who is elderly, disabled or a young child makes the
        # household targeted. The glossary defines disabled by benefit
        # receipt, as 7 CFR 271.2 does for SNAP: is_usda_disabled covers SSI,
        # Social Security disability and the veterans' categories. Disability
        # retirement, railroad, interim assistance and employer disability
        # benefits count only when the disability is permanent under Social
        # Security standards, which disability_benefits, railroad_benefits
        # and workers_compensation cannot show, so is_disabled stands in.
        p_targeted = p.payment.targeted
        person = spm_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period) | person("is_usda_disabled", period)
        targeted_member = person("nv_liheap_immigration_eligible", period) & (
            (age >= p_targeted.elderly_age)
            | disabled
            | (age < p_targeted.young_child_age_limit)
        )
        targeted = spm_unit.any(targeted_member)
        cap = table_cap + targeted * p_cap.targeted_supplement
        return min_(benefit, cap)
