from policyengine_us.model_api import *


class md_meap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP regular heating benefit"
    unit = USD
    defined_for = "md_meap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/MD_BenefitMatrix_2025.pdf",
        "https://dhs.maryland.gov/documents/OHEP/Advisory%20Board/FY26-MEAP-Benefit-Matrix-2-1-1.pdf",
        "https://dhs.maryland.gov/documents/OHEP/FY27-MEAP-Benefit-Matrices.pdf#page=1",
        "https://liheapch.acf.gov/docs/2025/state-plans/MD_Plan_2025.pdf#page=11",
        # PDF pages 9, 10, 11.
        "https://liheapch.acf.gov/docs/2026/state-plans/MD_Plan_2026.pdf#page=9",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.07",
    )
    documentation = (
        "Annual regular heating assistance, verified for state FY25 to FY27 (July "
        "2024 to June 2027), which periods 2025 to 2027 read at January 1. Earlier "
        "results are unverified backfilled estimates. No actual-bill cap applies. "
        "Kerosene uses the oil row (labeled Oil/Kerosene from FY27) and a grid-tied "
        "solar home uses the electricity row; heat-in-rent uses the building's known "
        "fuel row, an inference because no separate renter table is published. Other "
        "and unspecified fuels return zero as a coverage gap. Garrett County applies "
        "the plan's 1.1 multiplier with half-up rounding; the published FY27 Garrett "
        "table matches it in every cell but oil Level 4, which prints $1,210 where "
        "1.1 times $980 is $1,078. An unknown county receives the statewide amount. "
        "Means-tested VA eligibility remains unsupported. The $21 SNAP nominal "
        "payment, cooling, EUSP, arrearage, crisis and equipment benefits are "
        "excluded."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.payment
        # The floor keeps units outside Maryland (level 0) on a valid amount key.
        level = max_(spm_unit("md_meap_level", period), 1)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        # A grid-tied solar home pays an electricity bill, the pairing
        # heating_expense uses; manual 1.1.1 (page 6) lists solar subscriptions.
        amount = select(
            [
                (fuel == types.ELECTRICITY) | (fuel == types.SOLAR),
                fuel == types.NATURAL_GAS,
                (fuel == types.WOOD) | (fuel == types.COAL),
                (fuel == types.FUEL_OIL) | (fuel == types.KEROSENE),
                fuel == types.PROPANE,
            ],
            [
                p.amount.electricity[level],
                p.amount.gas[level],
                p.amount.wood_coal[level],
                p.amount.oil[level],
                p.amount.propane[level],
            ],
            # Other and unspecified fuels have no matrix row; the unspecified
            # default is tracked in #9754.
            default=0,
        )
        county = spm_unit.household("county_str", period)
        regional = np.isin(county, p.regional_counties) & (level != p.nominal_level)
        # Half-up rounding and the flat nominal amount follow the FY27 Garrett
        # table; FY25 and FY26 publish no Garrett dollar table.
        return np.floor(amount * where(regional, p.garrett_multiplier, 1) + 0.5)
