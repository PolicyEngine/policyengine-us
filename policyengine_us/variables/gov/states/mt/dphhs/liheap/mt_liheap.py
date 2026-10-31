from policyengine_us.model_api import *


class mt_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Montana LIHEAP regular heating benefit"
    documentation = "Annual Montana Low Income Home Energy Assistance Program regular heating benefit: the base benefit for the dwelling type, bedrooms and primary fuel times the income and heating degree day multiplier, with the modified benefit for publicly subsidized heat-in-rent households and the rent cap for other heat-in-rent households. Verified for FFY2026-FFY2027; earlier results use parameter backfilling and are unverified historical estimates."
    defined_for = "mt_liheap_eligible"
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/0074fe4c5989f116f77c281ac5736bf5b0f2facbfaf09daf76450ecad7fcdf47#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/b2add645c2eceddb643df5cdaf684339b968b43fc63b88f21ea882dfeb930366#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/5475239b875d29ebe7cf1f12b38458830f87a4a18c8dd600b7548603204fccd9#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/5389d31b170322ad8de7c67ca74832a2fe762425962ec410fe9a737193afe951#page=1",
        # PDF pages 1-2
        "https://rules.mt.gov/policy-library-documents/application/pdf/dee81e32e61aaa09299e3eab0f50b8fe584ba1a19bc7c4c2ad41ff760a7c5ef5#page=1",
        # PDF pages 57-59, 68, 71-74, 112, 122
        "https://web.archive.org/web/20260915040544/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=57",
        # PDF pages 57-58, 68, 71-72, 74, 114, 124
        "https://web.archive.org/web/20261015032646/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=57",
        # PDF pages 5, 10
        "https://liheapch.acf.gov/docs/2026/state-plans/MT_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap.payment
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # Kerosene, a deliverable fuel under ARM 37.70.401(5), uses the fuel
        # oil column. Heating assistance covers only propane, wood, coal, fuel
        # oil, natural gas and electricity, not solar (manual section 8.1 Fuel
        # Types), so SOLAR and OTHER pay $0, in non-traditional dwellings too.
        fuel_columns = [
            heating_type == fuel.NATURAL_GAS,
            heating_type == fuel.ELECTRICITY,
            heating_type == fuel.PROPANE,
            (heating_type == fuel.FUEL_OIL) | (heating_type == fuel.KEROSENE),
            heating_type == fuel.WOOD,
            heating_type == fuel.COAL,
        ]
        dwelling = spm_unit("mt_liheap_dwelling_type", period)
        dwellings = dwelling.possible_values
        # Physical bedrooms, at least one and no more than four (manual
        # section 3.21).
        bedrooms = clip(spm_unit.household("bedrooms", period), 1, p.max_bedrooms)
        base = p.base_benefit
        base_benefit = select(
            fuel_columns,
            [
                base.natural_gas[dwelling][bedrooms],
                base.electricity[dwelling][bedrooms],
                base.propane[dwelling][bedrooms],
                base.fuel_oil[dwelling][bedrooms],
                base.wood[dwelling][bedrooms],
                base.coal[dwelling][bedrooms],
            ],
            default=0,
        )
        multiplier = spm_unit("mt_liheap_multiplier", period)
        # Rounded to the nearest dollar ($1,503 x 0.83 = $1,247 in the
        # 2025-2026 manual, section 3.23). Non-traditional dwellings receive
        # one flat amount for each allowable fuel with no multiplier (manual
        # section 3.36: the benefit is not calculated); the fuel matrices hold
        # no row for them.
        regular = where(
            dwelling == dwellings.NON_TRADITIONAL,
            p.non_traditional_benefit,
            np.floor(base_benefit * multiplier + 0.5),
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # ARM 37.70.402(7) (numbered (6) from May 23, 2026) and 37.70.601(3):
        # publicly subsidized households with heat in their rent receive only
        # the modified benefit. The five-year eligibility period and the
        # branch for subsidized households paying only a base-load electric
        # bill (no input) are not modeled.
        modified = max_(p.modified.rate * regular, p.modified.minimum)
        # ARM 37.70.607(3): other heat-in-rent households receive one seventh
        # of the benefit per month, each month at most half of that month's
        # rent. Steady rent and receipts for every heating-season month are
        # assumed. Rent charged: `rent` nets out the modeled HUD
        # housing_assistance even for unsubsidized households.
        rent_cap = (
            p.heat_in_rent.rent_share
            * p.heat_in_rent.months
            * add(spm_unit, period, ["pre_subsidy_rent"])
            / MONTHS_IN_YEAR
        )
        amount = select(
            [heat_in_rent & subsidized, heat_in_rent],
            [modified, min_(regular, rent_cap)],
            default=regular,
        )
        # Not modeled: proration for movers and new residents (ARM
        # 37.70.602), wood and coal vendor or reimbursement mechanics,
        # reimbursement limited to paid costs when the account is not in a
        # member's name (ARM 37.70.607(2)), and credit balances.
        return where(np.any(fuel_columns, axis=0), amount, 0)
