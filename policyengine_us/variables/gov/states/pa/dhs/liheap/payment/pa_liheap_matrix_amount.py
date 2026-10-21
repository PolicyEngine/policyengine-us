from policyengine_us.model_api import *


class pa_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP benefit table heating payment"
    defined_for = StateCode.PA
    reference = (
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/638_LIHEAP_Program_Benefits/638.3_Benefit_Calculation.htm",
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/638_LIHEAP_Program_Benefits/Appendix_B__Minimum_and_Maximum_Benefit_Levels.htm",
        # PDF pages 1-469
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/PA_BenefitMatrix_2025.pdf#page=1",
        # PDF pages 1-469
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/PA_BenefitMatrix_2026.pdf#page=1",
        "https://www.humanservices.dhs.pa.gov/liheap_benefit_table/",
        # Section 601.41; PDF pages 38-39
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=38",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.payment
        county = spm_unit.household("county_str", period)
        region = select(
            [
                np.isin(county, p.regions.region_1),
                np.isin(county, p.regions.region_2),
                np.isin(county, p.regions.region_3),
                np.isin(county, p.regions.region_4),
                np.isin(county, p.regions.region_5),
            ],
            [1, 2, 3, 4, 5],
            default=0,
        )
        known_county = region > 0
        # The shared county variable defaults missing Pennsylvania geography
        # to Adams County. Explicit unknown counties remain unsupported here.
        safe_county = where(known_county, county, "ADAMS_COUNTY_PA")
        safe_region = max_(region, 1)
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # Handbook 638.3 fuel codes 701-708 have no solar code. A grid-tied
        # solar home pays an electricity bill, the pairing heating_expense uses,
        # so it takes the electric row. Propane shares the electric row.
        fuel_rows = [
            (heating_type == fuel.ELECTRICITY)
            | (heating_type == fuel.SOLAR)
            | (heating_type == fuel.PROPANE),
            heating_type == fuel.NATURAL_GAS,
            (heating_type == fuel.WOOD) | (heating_type == fuel.OTHER),
            heating_type == fuel.FUEL_OIL,
            heating_type == fuel.COAL,
            heating_type == fuel.KEROSENE,
        ]
        base = select(
            fuel_rows,
            [
                p.base.electricity[safe_region],
                p.base.natural_gas[safe_county],
                p.base.wood_other[safe_region],
                p.base.fuel_oil[safe_county],
                p.base.coal[safe_county],
                p.base.kerosene[safe_county],
            ],
            default=0,
        )
        priced_fuel = np.any(fuel_rows, axis=0)
        size = spm_unit("pa_liheap_household_size", period)
        # Handbook 638.3 household sizes run from 1 to 20; the printed tables
        # stop at 11.
        capped_size = min_(size, p.maximum_household_size)
        income = max_(spm_unit("pa_liheap_benefit_income", period), 0)
        multiplier = p.income_multiplier.calc(income)
        uncapped = multiplier * (base + p.additional_member_amount * (capped_size - 1))
        # Half-up rounding to whole dollars reproduces every printed cell;
        # round-half-to-even does not.
        amount = np.clip(np.floor(uncapped + 0.5), p.minimum, p.maximum)
        # This is an ungated table component, not the final award. Blended
        # fuel has no input.
        return where(known_county & priced_fuel & (size > 0), amount, 0)
