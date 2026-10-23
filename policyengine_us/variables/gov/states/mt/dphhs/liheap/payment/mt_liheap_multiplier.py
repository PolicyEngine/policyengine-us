from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mt_liheap_multiplier(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = "/1"
    label = "Montana LIHEAP income and heating degree day multiplier"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/0074fe4c5989f116f77c281ac5736bf5b0f2facbfaf09daf76450ecad7fcdf47#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/b2add645c2eceddb643df5cdaf684339b968b43fc63b88f21ea882dfeb930366#page=1",
        # PDF pages 57-59, 123
        "https://web.archive.org/web/20260915040544/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=57",
        # PDF pages 30, 58, 125
        "https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=30",
        "https://web.archive.org/web/20251117073831/https://www.dphhs.mt.gov/HCSD/energyassistance/index",
        "https://dphhs.mt.gov/HCSD/energyassistance/liheapoffices",
        "https://liheapch.acf.gov/docs/2026/state-plans/MT_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap
        size = spm_unit("mt_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1),
            state_group,
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        income = spm_unit("mt_liheap_benefit_income", period)
        # The manual's examples round the poverty ratio to a whole percent
        # (59% and 71% in the 2025-2026 edition).
        percent = np.floor(100 * income / guideline + 0.5)
        # Categorically eligible households above the income limit receive
        # the lowest multiplier (manual section 3.11; FY2026 plan item 1.6).
        categorical = spm_unit("mt_liheap_categorical_eligibility", period)
        over_limit = (categorical != categorical.possible_values.NONE) & (
            income > spm_unit("mt_liheap_income_limit", period)
        )
        # Each county belongs to one sub-grantee district; an unknown or
        # non-Montana county matches none and returns zero.
        county = spm_unit.household("county_str", period)
        multiplier = 0
        for district in p.payment.district:
            scale = p.payment.multiplier[district]
            band = where(over_limit, scale.thresholds[-1], percent)
            in_district = np.isin(county, p.payment.district[district])
            multiplier = multiplier + where(in_district, scale.calc(band), 0)
        return multiplier
