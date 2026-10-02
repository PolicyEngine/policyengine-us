from policyengine_us.model_api import *


class md_meap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP regular heating benefit"
    unit = USD
    defined_for = "md_meap_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/OHEP/Advisory%20Board/FY26-MEAP-Benefit-Matrix-2-1-1.pdf",
        # PDF pages 9, 10, 11.
        "https://liheapch.acf.gov/docs/2026/state-plans/MD_Plan_2026.pdf#page=9",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.07",
        "https://dhs.maryland.gov/documents/OHEP/FY27-MEAP-Benefit-Matrices.pdf#page=1",
    )
    documentation = "Annual regular heating assistance, verified for state FY26 (July 2025-June 2026), modeled in period 2026. Earlier results are unverified backfilled estimates. No actual-bill cap applies. Kerosene uses oil (explicitly labeled together in FY27); heat-in-rent uses the building's known fuel row, an inference because no separate renter table is published. Unknown fuels return zero; unknown county receives the statewide amount and cannot receive the Garrett supplement. Means-tested VA eligibility remains unsupported. Cooling, EUSP, arrearages, crisis and equipment benefits are excluded."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.payment
        level = spm_unit("md_meap_level", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        amount = select(
            [
                fuel == types.ELECTRICITY,
                (fuel == types.NATURAL_GAS)
                | (fuel == types.WOOD)
                | (fuel == types.COAL),
                (fuel == types.FUEL_OIL) | (fuel == types.KEROSENE),
                fuel == types.PROPANE,
            ],
            [
                p.amount.electricity[level],
                p.amount.gas_wood_coal[level],
                p.amount.oil[level],
                p.amount.propane[level],
            ],
            default=0,
        )
        county = spm_unit.household("county_str", period)
        regional = np.isin(county, p.regional_counties) & (level != p.nominal_level)
        # Half-up rounding and the flat nominal amount are inferred from the
        # later published Garrett table; no FY26 Garrett dollar table was found.
        return np.floor(amount * where(regional, p.garrett_multiplier, 1) + 0.5)
