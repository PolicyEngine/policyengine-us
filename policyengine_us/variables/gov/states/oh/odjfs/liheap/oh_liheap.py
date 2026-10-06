from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class oh_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Ohio HEAP regular heating assistance"
    defined_for = "oh_liheap_eligible"
    reference = (
        # Final 2021 workbook, physical pages 1, 8, 9 and 11.
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/OH_BenefitMatrix_2022.pdf#page=1",
        # Physical pages 1,8-11,15-16,19-20,29: factors, counties and formula.
        "https://liheapch.acf.gov/docs/2024/benefits-matricies/OH_BenefitMatrix_2024.pdf#page=1",
        # 2024 and 2025 draft workbook covers.
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/OH_BenefitMatrix_2025.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/OH_BenefitMatrix_2026.pdf#page=1",
        # Sections E-1, E-2, E-2.10 and E-4: income, disability and heating facts.
        "https://irp.cdn-website.com/aa88b0b1/files/uploaded/2022-24%20ATTACHMENT%202022-2023%20EAP%20Guidelines%20%281%29.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.odjfs.liheap
        payment = p.payment
        size = spm_unit("oh_liheap_household_size", period)
        guideline = fpg(
            max_(size, 1),
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        income = spm_unit("oh_liheap_countable_income", period)
        poverty_percentage = 100 * max_(
            income / guideline, payment.formula.minimum_poverty_ratio
        )
        # Coefficients follow the final 2021 and 2023 workbooks and the 2024
        # and 2025 draft workbooks; the 2025 values carry into 2026 and later as
        # unverified estimates (no 2026 workbook was found). Covers allow
        # 175% FPG but detailed tables end at 150%; extending the formula above
        # 150% is an explicitly approved estimate, not a sourced payment rule.
        # Annual income approximates the favorable 30-day/12-month comparison.
        # Guidelines still follow the requested year and state lag.
        base = max_(
            payment.formula.intercept - payment.formula.slope * poverty_percentage,
            0,
        )
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        fuel_ratio = select(
            [
                (heating_type == fuel.NATURAL_GAS) | (heating_type == fuel.ELECTRICITY),
                (heating_type == fuel.PROPANE)
                | (heating_type == fuel.FUEL_OIL)
                | (heating_type == fuel.KEROSENE),
                (heating_type == fuel.COAL) | (heating_type == fuel.WOOD),
            ],
            [
                payment.fuel_cost_ratio.gas_electricity,
                payment.fuel_cost_ratio.bulk_fuel,
                payment.fuel_cost_ratio.coal_wood,
            ],
            default=0,
        )
        county = spm_unit.household("county_str", period)
        regional = payment.regional
        regional_factor = select(
            [
                np.isin(county, regional.northern_counties),
                np.isin(county, regional.southern_counties),
                np.isin(county, regional.central_counties),
            ],
            [1 + regional.adjustment, 1 - regional.adjustment, 1],
            default=0,
        )
        targeting = payment.targeted
        age = spm_unit.members("age", period)
        # is_disabled approximates verified permanent and total disability.
        targeted_member = (age >= targeting.elderly_age) | spm_unit.members(
            "is_disabled", period
        )
        if targeting.young_child_in_effect:
            targeted_member = targeted_member | (age <= targeting.young_child_age)
        targeted = spm_unit.any(targeted_member)
        multiplier = where(targeted, targeting.multiplier, 1)
        # No existing input identifies PIPP enrollment: estimate the non-PIPP
        # award and leave its 75% reduction unmodeled. Unpriced fuel or an
        # explicit UNKNOWN or non-Ohio county returns an unsupported zero, not a
        # finding of legal ineligibility. An omitted county cannot be detected:
        # the county input then defaults to the state's alphabetically first
        # county, Adams, a southern county, so the estimate uses the 6% southern
        # reduction.
        # The 2023 gas ratio has four decimals; some 2023 table cells differ by
        # $1. Final half-up rounding matches the other printed fuel calculations;
        # do not round a component before the regional and targeted adjustments.
        return np.floor(base * fuel_ratio * regional_factor * multiplier + 0.5)
