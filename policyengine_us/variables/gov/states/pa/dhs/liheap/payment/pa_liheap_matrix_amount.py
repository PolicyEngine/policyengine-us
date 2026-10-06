from policyengine_us.model_api import *


class pa_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP published heating payment"
    defined_for = StateCode.PA
    reference = (
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/PA_BenefitMatrix_2025.pdf#page=1",
        # Section 1.1 dates of operation: FY2025 heating assistance opens 11/04/2024.
        "https://liheapch.acf.gov/docs/2025/state-plans/PA_Plan_2025.pdf#page=4",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/PA_BenefitMatrix_2026.pdf#page=1",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=31",
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/638_LIHEAP_Program_Benefits/638.3_Benefit_Calculation.htm",
        "https://www.humanservices.dhs.pa.gov/liheap_benefit_table/",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=5",
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
        safe_region = np.clip(region, 1, 5)
        size = spm_unit("pa_liheap_household_size", period)
        income = spm_unit("pa_liheap_benefit_income", period)
        safe_size = np.clip(size, 1, p.maximum_household_size)
        safe_band = np.clip(
            np.floor(max_(income, 0) / p.band_width).astype(int),
            0,
            p.income_band_count - 1,
        )
        # Every terminal cell in the FY2025, FY2026 and FY2027 schedules equals
        # the $200 minimum. The current lookup is undated; its FY2027 observation
        # follows the adopted plan and handbook links, with the November 2, 2026
        # season start.
        # The handbook's nonincreasing income multipliers and minimum imply the
        # payment above the printed income range for supported household sizes.
        # This is a deduction from the rules and table, not a printed extension.
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # Handbook 638.3 fuel codes 701-708 have no solar code. A grid-tied
        # solar home pays an electricity bill, the pairing heating_expense uses,
        # so it takes the electric row.
        electric = (
            (heating_type == fuel.ELECTRICITY)
            | (heating_type == fuel.SOLAR)
            | (heating_type == fuel.PROPANE)
        )
        amount = select(
            [
                electric,
                heating_type == fuel.NATURAL_GAS,
                (heating_type == fuel.WOOD) | (heating_type == fuel.OTHER),
                heating_type == fuel.FUEL_OIL,
                heating_type == fuel.COAL,
                heating_type == fuel.KEROSENE,
            ],
            [
                p.matrix.electricity_propane[safe_region][safe_band][safe_size],
                p.matrix.natural_gas[safe_county][safe_band][safe_size],
                p.matrix.wood_other[safe_region][safe_band][safe_size],
                p.matrix.fuel_oil[safe_county][safe_band][safe_size],
                p.matrix.coal[safe_county][safe_band][safe_size],
                p.matrix.kerosene[safe_county][safe_band][safe_size],
            ],
            default=0,
        )
        supported_bounds = (
            known_county
            & (size >= 1)
            & (size <= p.maximum_household_size)
            & (income >= 0)
        )
        # This is an ungated payment-table component, not the final award.
        # Zero for unsupported sizes, counties or fuels is an unverified
        # placeholder, not legal ineligibility. Blended fuel lacks an input;
        # size 12+ remains unverified.
        return where(supported_bounds, amount, 0)
